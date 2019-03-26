from . import VitrualBlock, User
import threading

class VersionNode(object):
    
    def __init__(self, base_rev, rev, modifier, modified_time, size, isconflict):
        self.base_rev = base_rev
        self.rev = rev
        self.modifier = modifier
        self.modified_time = modified_time
        self.size = size
        self.isconflict = isconflict
        self.blocks = []
        self.temporary = True
        self.lock = threading.RLock()

    def to_dict(self):
        self.lock.acquire()
        dict = {}
        dict['base_rev'] = self.base_rev
        dict['rev'] = self.rev
        dict['modifier'] = self.modifier.__dict__
        dict['modified_time'] = self.modified_time
        dict['size'] = self.size
        dict['isconflict'] = self.isconflict
        dict['temporary'] = self.temporary
        blocks = []
        for block in self.blocks:
            blocks.append(block.to_dict())
        dict['blocks'] = blocks
        self.lock.release()
        return dict

    def add_vitrual_block(self, block):
        self.lock.acquire()
        self.blocks.append(block)
        self.lock.release()

    def read_data(self, block_index):
        self.lock.acquire()
        b, o, c = self.blocks[block_index].read_data()
        self.lock.release()
        if c is not None:
            return None, None, c
        else:
            return b, o, c

    def isTemporary(self):
        self.lock.acquire()
        temporary = self.temporary
        self.lock.release()
        return temporary

    def setTemporary(self, t):
        self.lock.acquire()
        self.temporary = t
        self.lock.release()

    def read_hash_list(self):
        self.lock.acquire()
        list = []
        for vblock in self.blocks:
            list.append(vblock.get_hash())
        self.lock.release()
        return list

def from_dict(dict):
    base_rev = dict.get('base_rev')
    rev = dict.get('rev')
    modifier = User.from_dict(dict.get('modifier'))
    modified_time = dict.get('modified_time')
    size = dict.get('size')
    isconflict = dict.get('isconflict')
    vnode = VersionNode(base_rev, rev, modifier, modified_time, size, isconflict)
    for block in dict.get('blocks'):
        vnode.add_vitrual_block(VitrualBlock.from_dict(block))
    vnode.temporary = dict.get('temporary')
    return vnode


