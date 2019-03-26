from . import VitrualBlock, User

class VersionNode(object):
    
    def __init__(self, base_rev, rev, modifier, modified_time, size):
        self.base_rev = base_rev
        self.rev = rev
        self.modifier = modifier
        self.modified_time = modified_time
        self.size = size
        self.blocks = []
        self.temporary = True

    def to_dict(self):
        dict = {}
        dict['base_rev'] = self.base_rev
        dict['rev'] = self.rev
        dict['modifier'] = self.modifier.__dict__
        dict['modified_time'] = self.modified_time
        dict['size'] = self.size
        dict['temporary'] = self.temporary
        blocks = []
        for block in self.blocks:
            blocks.append(block.to_dict())
        dict['blocks'] = blocks
        return dict

    def add_vitrual_block(self, block):
        self.blocks.append(block)

    def read_data(self, block_index):
        b, o, c = self.blocks[block_index].read_data()
        if c is not None:
            return None, None, c
        else:
            return b, o, c

def from_dict(dict):
    base_rev = dict.get('base_rev')
    rev = dict.get('rev')
    modifier = User.from_dict(dict.get('modifier'))
    modified_time = dict.get('modified_time')
    size = dict.get('size')
    vnode = VersionNode(base_rev, rev, modifier, modified_time, size)
    for block in dict.get('blocks'):
        vnode.add_vitrual_block(VitrualBlock.from_dict(block))
    vnode.temporary = dict.get('temporary')
    return vnode


