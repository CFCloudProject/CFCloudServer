import pickle
import json
import os
import config
import versions

class metadata(object):

    def __init__(self, attributes, path, _versions = None):
        # attributes: 
        #   tag                 string      ('file', 'folder')
        #   name                string
        #   fullpath            string
        #   size                int
        #   rev                 int         (start from 0)
        #   creation_time       int         (UTC ticks)
        #   modified_time       int         (UTC ticks)
        #   modifier            dict        (include user_id, email, firstname, lastname)
        #   owner               dict        (include user_id, email, firstname, lastname)
        #   shared_users        list of dict
        #   is_shared           bool
        #   is_deleted          bool
        self.attributes = attributes
        if _versions is None:
            if self.attributes['tag'] == 'file':
                self.versions = versions.versions()
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

    def get_hashlist(self, rev = None):
        if self.attributes['tag'] == 'folder':
            return None
        return self.versions.get_hashlist(rev)








    '''
    def create_temp_version(self, modifier, modified_time, size, base_rev):
        self.lock.acquire()
        rev = self.versions.add_temporary_node(modifier, modified_time, size, base_rev)
        if base_rev is None:
            haselist = []
        else:
            r, hashlist = self.versions.read_hash_list(base_rev)
        self.dirty = True
        self.lock.release()
        return rev, hashlist

    def add_vitrual_block(self, rev, block):
        self.lock.acquire()
        self.versions.add_vitrual_block(rev, block)
        self.dirty = True
        self.lock.release()

    def add_vitrual_blocks(self, rev, blocks):
        self.lock.acquire()
        self.versions.add_vitrual_blocks(rev, blocks)
        self.dirty = True
        self.lock.release()

    def read_block(self, rev, index):
        self.lock.acquire()
        data = self.versions.read_block(index, rev)
        self.lock.release()
        return data

    def read_blocks(self, rev, indexs):
        self.lock.acquire()
        for index in indexs:
            yield self.versions.read_block(index, rev)
        self.lock.release()

    def set_readable(self, rev):
        self.lock.acquire()
        version, size, time, modifier = self.versions.set_readable(rev)
        self.attributes['rev'] = version
        self.attributes['size'] = size
        self.attributes['modified_time'] = time
        self.attributes['modifier'] = modifier
        self.dirty = True
        self.lock.release()

    def share(self, user):
        self.lock.acquire()
        self.attributes['is_shared'] = True
        self.attributes['sharedusers'].append(user)
        self.dirty = True
        self.lock.release()
    '''






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
    return metadata(dict['attributes'], dict['path'])