from . import VersionNode
from OT import OTFunctions
import Global
import threading

class VersionVector(object):
    
    def __init__(self):
        self.w_rev = -1
        self.r_rev = -1
        self.vector = []
        self.lock = threading.RLock()

    def to_dict(self):
        self.lock.acquire()
        dict = {}
        dict['size'] = self.size
        dict['w_rev'] = self.w_rev
        dict['r_rev'] = self.r_rev
        vector = []
        for rev in self.vector:
            vector.append(rev.to_dict())
        dict['vector'] = vector
        self.lock.release()
        return dict

    def add_temporary_node(self, modifier, modified_time, size, base_rev):
        self.lock.acquire()
        self.w_rev += 1
        vnode = VersionNode.VersionNode(base_rev, self.w_rev, modifier, modified_time, size, base_rev < self.r_rev)
        self.vector.append(vnode)
        if base_rev < self.r_rev:
            self.w_rev += 1
            vnode = VersionNode.VersionNode(0, self.w_rev, Global._server_user, modified_time, 0, False)
            self.lock.release()
            return self.w_rev - 1
        else:
            self.lock.release()
            return self.w_rev

    def add_vitrual_block(self, rev, block):
        self.lock.acquire()
        vnode = self.vector[rev]
        vnode.add_vitrual_block(block)
        self.lock.release()

    def __update_r_rev(self):
        self.lock.acquire()
        while self.r_rev < self.w_rev:
            if not self.vector[self.r_rev + 1].isTtemporary():
                self.r_rev += 1
            else:
                break
        self.lock.release()

    def set_readable(self, rev):
        self.lock.acquire()
        vnode = self.vector[rev]
        if vnode.isTemporary():
            vnode.setTemporary(False)
        if vnode.isconflict:
            self.__resolve_conflict(rev)
        self.__update_r_rev()
        vnode = self.vector[self.r_rev]
        self.lock.release()
        return self.r_rev, vnode.size, vnode.modified_time, vnode.modifier

    def __resolve_conflict(self, rev):
        pass

    def read_hash_list(self, rev = None):
        self.lock.acquire()
        if rev is None:
            rev = self.r_rev
        if rev < 0:
            hashlist = None
        else:
            vnode = self.vector[rev]
            hashlist = vnode.read_hash_list()
        self.lock.release()
        return rev, hashlist

    def read_block(self, block_index, rev = None):
        self.lock.acquire()
        if rev is None:
            rev = self.r_rev
        if rev < 0:
            self.lock.release()
            return None
        b, o, c = self.vector[rev].read_data(block_index)
        if c is not None:
            data = c
        else:
            if b is None:
                data = None
            else:
                bindex = bin.split(':')
                base_rev = int(binex[0])
                base_index = int(bindex[1])
                base_data = self.read_block(base_index, base_rev)
                if base_data is None:
                    data = None
                elif o is None:
                    data = base_data
                else:
                    data = ExecuteOpList(base_data, o)
        self.lock.release()
        return data

    def write_block(self, base_rev, rev, base_index, index, confidence, hash, data):
        self.lock.acquire()

        self.lock.release()

def from_dict(dict):
    vv = VersionVector()
    vv.size = dict.get('size')
    vv.r_rev = dict.get('r_rev')
    vv.w_rev = dict.get('w_rev')
    for v_dict in dict.get('vector'):
        vv.vector.append(VersionNode.from_dict(v_dict))
    return vv