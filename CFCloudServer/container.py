import config
import server_init
import utils

class container(object):

    def __init__(self, container_id, data = None):
        self.id = container_id
        if data is None:
            self.data = b''
            self.dirty = True
        else:
            self.data = data
            self.dirty = False

    def read_block(self, block):
        if block['container_id'] != self.id:
            return None
        offset = block['offset']
        if self.data[offset : offset + 20].hex() != block['block_id']:
            return None
        offset += 20
        size = self.data[offset : offset + 2]
        size = size[0] * 256 + size[1]
        if size != block['size']:
            return None
        offset += 2
        return self.data[offset : offset + size]

    def write_block(self, block_id, data):
        data_head = bytes.fromhex(block_id)
        size = len(data)
        data_size = utils.int2bytes(size)
        data_to_write = data_head + data_size + data
        offset = len(self.data)
        if offset + size + 22 > config.container_max_size:
            # need to split psi node
            return None
        self.data = self.data + data_to_write
        self.dirty = True
        return { 
            'block_id': block_id, 
            'container_id': self.id, 
            'offset': offset, 
            'size': size 
            }

    # hashs: hash of blocks that will be reserved in the current container
    def split(self, hashs):
        # create new container
        container_id = utils.get_new_container_id()
        cnode = server_init._container_cache.get_usable_node(container_id)
        cnode.acquire_lock()
        cnode.create(container_id)
        # split data
        data = self.data
        self.data = b''

        offset_cur = 0
        offset_new = 0
        blocks_to_update = []
        pos = 0

        while pos < len(data):
            hash = data[pos : pos + 20].hex()
            size = data[pos + 20] * 256 + data[pos + 21]
            if hash in hashs:
                self.data = self.data + data[pos : pos + size + 22]
                blocks_to_update.append({
                    'block_id': hash,
                    'container_id': self.id,
                    'offset': offset_cur,
                    'size': size
                    })
                offset_cur += size + 22
            else:
                cnode.obj.data = cnode.obj.data + data[pos : pos + size + 22]
                blocks_to_update.append({
                    'block_id': hash,
                    'container_id': container_id,
                    'offset': offset_new,
                    'size': size
                    })
                offset_new += size + 22
            pos += size + 22

        data = None
        cnode.release_lock()
        self.dirty = True
        return container_id, blocks_to_update
    
    def write_back(self):
        key = 'Container_' + str(self.id)
        if not self.dirty:
            return True
        else:
            ret = server_init._s3_connector.upload(key, self.data)
            if ret:
                self.dirty = False
                return True
            else:
                return False

def load(container_id):
    key = 'Container_' + str(container_id)
    data = server_init._s3_connector.download(key)
    if data is None:
        return None
    _container = container(container_id, data)
    return _container

def create(container_id):
    return container(container_id)