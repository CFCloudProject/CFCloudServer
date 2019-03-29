import vnode

class versions(object):
    
    def __init__(self):
        self.w_rev = -1
        self.r_rev = -1
        self.vector = []

    def get_hashlist(self, rev = None):
        if rev is None:
            rev = self.r_rev
        return self.vector[rev].get_hastlist()

    def get_size_hashs(self):
        size = 0
        hashs = []
        for version in self.vector:
            (_size, _hashs) = version.get_size_hashs()
            size += _size
            hashs.extend(_hashs)
        return { 'size': size, 'hashs': hashs }















    '''
    def add_temporary_node(self, modifier, modified_time, size, base_rev):
        self.lock.acquire()
        conflict = base_rev < self.w_rev
        self.w_rev += 1
        vnode = VersionNode.VersionNode(base_rev, self.w_rev, modifier, modified_time, size, conflict)
        self.vector.append(vnode)
        self.lock.release()
        return self.w_rev

    def add_vitrual_block(self, rev, block):
        self.lock.acquire()
        vnode = self.vector[rev]
        vnode.add_vitrual_block(block)
        self.lock.release()

    def add_vitrual_blocks(self, rev, blocks):
        self.lock.acquire()
        vnode = self.vector[rev]
        for block in blocks:
            vnode.add_vitrual_block(block)
        self.set_readable(rev)
        self.lock.release()

    def __update_r_rev(self):
        while self.r_rev < self.w_rev:
            if not self.vector[self.r_rev + 1].isTtemporary():
                self.r_rev += 1
            else:
                break

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
    '''

    def to_dict(self):
        dict = {}
        dict['w_rev'] = self.w_rev
        dict['r_rev'] = self.r_rev
        dict['vector'] = []
        for _vnode in self.vector:
            dict['vector'].append(_vnode.__dict__)
        return dict

def from_dict(dict):
    _versions = versions()
    _versions.r_rev = dict.get('r_rev')
    _versions.w_rev = dict.get('w_rev')
    vector = dict.get('vector')
    for v_dict in vector:
        _versions.vector.append(vnode.from_dict(v_dict))
    return _versions