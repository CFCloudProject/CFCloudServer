import server_init
import config
import utils
import pickle
import os
import uuid

class psinode(object):

    def __init__(self, type, id, paths, container_ids):
        self.type = type
        self.id = id
        self.paths = paths
        self.container_ids = container_ids
        self.dirty = True

    def write_block(self, path, block_id, data):
        container_id = self.container_ids[len(self.container_ids) - 1]
        cnode = server_init._container_cache.get_usable_node(container_id)
        cnode.acquire_lock()
        # if the container in the container cache node is not the target one, reload
        if not cnode.obj.id == container_id:
            cnode.load(container_id)
        w_ret = cnode.obj.write_block(block_id, data)
        if w_ret is not None:
            server_init._block_index.insert(w_ret)
            r_psid = self.id
        else:
            # the container has reached max size; 
            # need to split psi node (for type 'a' and 'b')
            # or add new container (for type 'c')
            psid = self.split(path, cnode)
            r_psid = psid
            if psid == self.id:
                self.write_block(path, block_id, data)
            else:
                pnode = server_init._psi_cache.get_usable_node(psid)
                pnode.acquire_lock()
                if not pnode.obj.id == psid:
                    pnode.load(psid)
                pnode.obj.write_block(path, block_id, data)
                pnode.release_lock()
        cnode.release_lock()
        return r_psid

    # return the id of the psi node that the data will be write to
    def split(self, path, cnode):
        # psinode of type 'c' do not need to split
        if self.type == 'c':
            # simply add a new container
            container_id = utils.get_new_container_id()
            self.container_ids.append(container_id)
            _cnode = server_init._container_cache.get_usable_node(container_id)
            _cnode.acquire_lock()
            _cnode.create(container_id)
            _cnode.release_lock()
            return self.id
        else:
            # split the psinode to 2
            if self.type == 'a':
                # first, find the path that will occur in the 2 result psinodes' path set
                #        for type 'a', path set only include one path which is a folder, 
                #        and the argument path is a file, so they should not equal
                singlepathset = self.paths[0]
                while not os.path.dirname(path) == singlepathset:
                    path = os.path.dirname(path)
                #        for type 'a', change its path to its child set
                server_init._psi.delete_by_filepath(self.paths[0])
                self.paths = []
                for child in os.listdir(singlepathset):
                    if child == '.metadata':
                        continue
                    elif child.endswith('.metadata'):
                        self.paths.append('/'.join([singlepathset, child[:-9]]))
                    else:
                        self.paths.append('/'.join([singlepathset, child]))
            else:
                # first, find the path that will occur in the 2 result psinodes' path set
                #        for type b, path itself or one of its ancestors is in self.paths
                while not path in self.paths:
                    path = os.path.dirname(path)
            # second, get all total sizes and hashs of all paths in path set
            list_for_sort = []
            for _path in self.paths:
                if os.path.isdir(_path):
                    meta_path = _path + '/.metadata'
                else:
                    meta_path = _path + '/.metadata'
                mnode = server_init._metadata_cache.get_usable_node(meta_path)
                mnode.acquire_lock()
                if not mnode.obj.path == meta_path:
                    mnode.load(meta_path)
                t = mnode.obj.get_size_hashs()
                t['path'] = _path
                list_for_sort.append(t)
                mnode.release_lock()
            # third, sort the list by total size
            list_for_sort.sort(key=lambda t: t['size'], reverse=True)
            # forth, split the list to two parts
            #        the largest one is reserved in the current psinode,
            #        remains are add to the small psinode one by one
            psid = str(uuid.uuid1())
            pnode = server_init._psi_cache.get_usable_node(psid)
            pnode.acquire_lock()
            size_left = 0
            size_right = 0
            paths_left = []
            paths_right = []
            hashs_to_reserve = []
            for t in list_for_sort:
                if size_left <= size_right:
                    paths_left.append(t['path'])
                    if self.type == 'a':
                        server_init._psi.insert(t['path'], self.id)
                    else:
                        server_init._psi.update(t['path'], self.id)
                    size_left += t['size']
                    hashs_to_reserve.extend(t['hashs'])
                else:
                    paths_right.append(t['path'])
                    if self.type == 'a':
                        server_init._psi.insert(t['path'], psid)
                    else:
                        server_init._psi.update(t['path'], psid)
                    size_right += t['size']
            if not path in self.paths:
                if size_left <= size_right:
                    path_left.append(path)
                    server_init._psi.insert(path, self.id)
                else:
                    path_right.append(path)
                    server_init._psi.insert(path, psid)
            # fifth, using the splited hashs to split the container (argument cnode)
            #        and get the id of the new container
            (container_id, blocks) = cnode.obj.split(hashs_to_reserve)
            # sixth, update block index
            server_init._block_index.update_list(blocks)
            # seventh, update current psinode and create new psinode
            self.paths = paths_left
            if len(paths_left) > 1:
                self.type = 'b'
            elif os.path.isdir(paths_left[0]):
                self.type = 'a'
            else:
                self.type = 'c'
            self.dirty = True
            if len(paths_right) > 1:
                type = 'b'
            elif os.path.isdir(paths_right[0]):
                type = 'a'
            else:
                type = 'c'
            pnode.create({
                'type': type,
                'id': psid,
                'paths': paths_right, 
                'container_ids': [container_id]
                })
            pnode.release_lock()
            # eighth, decide which psinode's id to be return
            if path in self.paths:
                return self.id
            else:
                return psid

    def write_back(self):
        if self.dirty:
            psipath = config.psi_root + '/' + self.id + '.psi'
            fp = open(psipath, 'wb')
            pickle.dump(self.__dict__, fp)
            fp.close()
            self.dirty = False

def load(psid):
    psipath = config.psi_root + '/' + psid + '.psi'
    if os.path.exists(psipath):
        fp = open(psipath, 'rb')
        attr = pickle.load(fp)
        fp.close()
        node = create(attr)
        node.dirty = False
        return node

def create(attr):
    return psinode(attr['type'], attr['id'], attr['paths'], attr['container_ids'])

