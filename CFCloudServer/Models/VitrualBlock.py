import threading
import Global
from OT import OTFunctions

class VitrualBlock(object):
    
    def __init__(self, base = None, op = None, current = None, hash = None):
        self.base = base
        self.op = op
        self.current = current
        self.hash = hash
        self.lock = threading.RLock()

    def get_hash(self):
        self.lock.acquire()
        hash = self.hash
        self.lock.release()
        return hash

    def read_data(self):
        self.lock.acquire()
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
        b = self.base
        self.lock.release()
        #return base_index, oplist, current_data
        return b, o, c

    def to_dict(self):
        self.lock.acquire()
        dict = {}
        if self.base is not None:
            dict['base'] = self.base
        if self.op is not None:
            dict['op'] = self.op
        if self.current is not None:
            dict['current'] = self.current
        if self.hash is not None:
            dict['hash'] = self.hash
        self.lock.release()
        return dict

def from_dict(dict):
    base = dict.get('base')
    op = dict.get('op')
    current = dict.get('current')
    hash = dict.get('hash')
    return VitrualBlock(base, op, current, hash)