import Global
from OT import OTFunctions

class VitrualBlock(object):
    
    def __init__(self, base_index = None, op_index = None, current_index = None, hash = None):
        self.base_index = base_index
        self.op_index = op_index
        self.current_index = current_index
        self.hash = hash

    def read_data(self):
        if self.current_index is not None:
            block = Global._BlockIndex.select(self.current_index)
            if block is None:
                return None
            return Global._container_cache.read_block(block)
        else:
            base_block = Global._BlockIndex.select(self.base_index)
            if base_block is None:
                return None
            op_block = Global._BlockIndex.select(self.op_index)
            if op_block is None:
                return None
            base = Global._container_cache.read_block(base_block)
            op = Global._container_cache.read_block(op_block)
            oplist = bytes2oplist(op)
            return ExecuteOpList(base, oplist)