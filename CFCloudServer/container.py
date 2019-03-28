import config
import utils
import variables

class container(object):

    def __init__(self, container_id = None):
        if container_id is None:
            self.id = utils.get_new_container_id()
            self.data = b''
            self.dirty = True
        else:
            self.id = container_id
            self.dirty = False

    def write_back(self):
        key = 'Container_' + str(self.id)
        if not self.dirty:
            return True
        else:
            ret = variables._s3_connector.upload(key, self.data)
            if ret:
                self.dirty = False
                return True
            else:
                return False

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

def load(container_id):
    key = 'Container_' + str(container_id)
    data = variables._s3_connector.download(key)
    if data is None:
        return None
    _container = container(container_id)
    _container.data = data
    return _container

def create():
    return container()