import Global
from OT import OTFunctions

class VitrualBlock(object):
    
    def __init__(self, base = None, op = None, current = None, hash = None):
        self.base = base
        self.op = op
        self.current = current
        self.hash = hash

    def read_data(self):
        if self.current is not None:
            block = Global._BlockIndex.select(self.current)
            if block is None:
                c = None
            else:
                c = Global._container_cache.read_block(block)
                return None, None, c
        if self.op is not None:
            op_block = Global._BlockIndex.select(self.op)
            if op_block is None:
                o = None
            else:
                o = Global._container_cache.read_block(op_block)
                o = bytes2oplist(o)
        #return base_index, oplist, current_data
        return self.base, o, c

    def to_dict(self):
        dict = {}
        if self.base is not None:
            dict['base'] = self.base
        if self.op is not None:
            dict['op'] = self.op
        if self.current is not None:
            dict['current'] = self.current
        dict['hash'] = self.hash
        return dict

def from_dict(dict):
    base = dict.get('base')
    op = dict.get('op')
    current = dict.get('current')
    hash = dict.get('hash')
    return VitrualBlock(base, op, current, hash)