class VersionNode(object):
    
    def __init__(self, ver=None, modifier=None, modified_time=None, size=None):
        self.ver = ver
        self.modifier = modifier
        self.modified_time = modified_time
        self.size = size
        self.blocks = []

    def set_ver(self, ver):
        self.ver = ver

    def set_modifier(self, modifier):
        self.modifier = modifier

    def set_modified_time(self, modified_time):
        self.modified_time = modified_time

    def set_size(self, size):
        self.size = size

    def add_vitrual_block(self, block):
        self.blocks.append(block)

    def read_data(self):
        ret = b''
        for block in self.blocks:
            ret += block.read_data()
        return ret


