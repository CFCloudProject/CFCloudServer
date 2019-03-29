

class vnode(object):
    
    def __init__(self, attributes, is_checkpoint, hashs, ops):
        # attributes: 
        #   size                int
        #   op_size             int
        #   base_rev            int
        #   rev                 int
        #   modifier            dict
        #   modified_time       int             (UTC ticks)
        self.attributes = attributes

        #   is_checkpoint       bool            (if is checkpoint, ops is None 
        #                                        and hashs represents for real stored blocks)
        self.is_checkpoint = is_checkpoint

        #   hashs               list of string  (hex mode hash which len is 40, 
        #                                        8 for adler32 and 32 for md5)
        self.hashs = hashs

        #   ops                 list of string  (hashs of op file blocks)
        self.ops = ops

    def get_hashlist(self):
        return self.hashs

    def get_size_hashs(self):
        if self.is_checkpoint:
            return self.attributes['size'], self.hashs
        else:
            return self.attributes['op_size'], self.ops

    '''
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
    '''

def from_dict(dict):
    return vnode(dict['attributes'], 
                 dict['is_checkpoint'], 
                 dict['hashs'], 
                 dict['ops'])


