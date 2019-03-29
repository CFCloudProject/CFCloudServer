import server_init

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

    def set_attribute(self, name, attr):
        self.attributes[name] = attr

    def get_attribute(self, name):
        attr = self.attributes[name]
        return attr

    def get_metadata(self):
        return self.attributes['size'], self.attributes['modified_time'], self.attributes['modifier']

    def get_hashlist(self):
        return self.hashs

    def get_size_hashs(self):
        if self.is_checkpoint:
            return self.attributes['size'], self.hashs
        else:
            return self.attributes['op_size'], self.ops

    def read(self):
        if self.is_checkpoint:
            hashs = self.hashs
        else:
            hashs = self.ops
        blocks = server_init._block_index.select_list(hashs)
        datas = {}
        for key in blocks.keys():
            cnode = server_init._container_cache.get_usable_node(key)
            cnode.acquire_lock()
            for block in blocks[key]:
                datas[block['block_id']] = cnode.obj.read_block(block)
            cnode.release_lock()
        data = b''
        for hash in hashs:
            data = data + datas[hash]
        return data

def from_dict(dict):
    return vnode(dict['attributes'], 
                 dict['is_checkpoint'], 
                 dict['hashs'], 
                 dict['ops'])


