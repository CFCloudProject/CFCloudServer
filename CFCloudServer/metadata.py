import pickle
import json
import os
import copy
import config
import versions
import server_init

class metadata(object):

    def __init__(self, attributes, path, _versions = None, optype = None):
        # attributes: 
        #   tag                 string      ('file', 'folder')
        #   name                string
        #   fullpath            string
        #   size                int
        #   rev                 int         (start from 0)
        #   creation_time       int         (Unix ticks)
        #   modified_time       int         (Unix ticks)
        #   modifier            dict        (include user_id, email, firstname, lastname)
        #   owner               dict        (include user_id, email, firstname, lastname)
        #   shared_users        list of dict
        #   is_shared           bool
        #   is_deleted          bool
        self.attributes = attributes
        if _versions is None:
            if self.attributes['tag'] == 'file':
                self.versions = versions.versions(optype)
            else:
                self.versions = None
        else:
            self.versions = _versions
        self.path = path
        self.dirty = True

    def set_attribute(self, name, attr):
        self.attributes[name] = attr
        self.dirty = True

    def get_attribute(self, name):
        attr = self.attributes[name]
        return attr

    def get_metadata(self):
        # return a json string that can be directly return to client
        return json.dumps(self.attributes)

    def get_metadata_by_version(self, rev):
        attr = copy.deepcopy(self.attributes)
        attr['rev'] = rev
        (size, modified_time, modifier) = self.versions.get_rev_metadata(rev)
        attr['size'] = size
        attr['modified_time'] = modified_time
        attr['modifier'] = modifier
        return json.dumps(attr)

    def get_hashlist(self, rev = None):
        if self.attributes['tag'] == 'folder':
            return None
        return self.versions.get_hashlist(rev)

    def get_offsets(self, rev = None):
        if self.attributes['tag'] == 'folder':
            return None
        return self.versions.get_offsets(rev)

    # get total size and all hashs of its all versions (file)
    # or the sum of its all children (folder)
    def get_size_hashs(self):
        if self.attributes['tag'] == 'folder':
            size = 0
            hashs = []
            path = self.path[:-10]
            for child in os.listdir(path):
                if child == '.metadata':
                    continue
                elif child.endswith('.metadata'):
                    child_path = '/'.join([path, child])
                else:
                    child_path = '/'.join([path, child]) + '.metadata'
                mnode = server_init._metadata_cache.get_usable_node(meta_path)
                mnode.acquire_lock()
                if mnode.empty or not mnode.obj.path == child_path:
                    mnode.load(child_path)
                t = mnode.obj.get_size_hashs()
                size += t['size']
                hashs.extend(t['hashs'])
            return { 'size': size, 'hashs': hashs }
        else:
            return self._versions.get_size_hashs()

    def add_vnode(self, node):
        hashs, datas = self.versions.add_vnode(node)
        if hashs is not None:
            psid = server_init._psi.get_psid_by_filepath(self.path[:-9])
            pnode = server_init._psi_cache.get_usable_node(psid)
            pnode.acquire_lock()
            if pnode.empty or not pnode.obj.id == psid:
                pnode.load(psid)
            for i in range(0, len(hashs)):
                if not server_init._hash_cache.search(hashs[i]):
                    r_psid = pnode.obj.write_block(self.path[:-9], hashs[i], datas[i])
                    if not r_psid == psid:
                        pnode.release_lock()
                        psid = r_psid
                        pnode = server_init._psi_cache.get_usable_node(psid)
                        pnode.acquire_lock()
                        if pnode.empty or not pnode.obj.id == psid:
                            pnode.load(psid)
            pnode.release_lock()
        self.set_attribute('rev', self.versions.rev)
        (size, modified_time, modifier) = self.versions.get_rev_metadata()
        self.set_attribute('size', size)
        self.set_attribute('modified_time', modified_time)
        self.set_attribute('modifier', modifier)
        self.dirty = True

    def read(self, rev = None):
        return self.versions.read(rev)

    def to_dict(self):
        dict = {}
        dict['attributes'] = self.attributes
        if self.versions is not None:
            dict['versions'] = self.versions.to_dict()
        return dict

    def write_back(self):
        if self.dirty:
            fp = open(self.path, 'wb')
            pickle.dump(self.to_dict(), fp)
            fp.close()
            self.dirty = False

def load(path):
    if(os.path.exists(path)):
        fp = open(path, 'rb')
        dict = pickle.load(fp)
        fp.close()
        _versions = None if dict.get('versions') is None else versions.from_dict(dict['versions'])
        meta = metadata(dict['attributes'], path, _versions)
        meta.dirty = False
        return meta
    else:
        return None

def create(dict):
    return metadata(dict['attributes'], dict['path'], optype=dict['optype'])