import Global
import Block
import six

class Container(object):

    def __init__(self, container_id = None):
        if container_id is None:
            self.id = Global.get_new_container_id()
            self.data = b''
            self.fragments = []
            self.dirty = False
        else:
            self.id = container_id

    def IsDirty(self):
        return self.dirty

    def write_back(self):
        key = 'Container_' + str(self.id)
        if not self.dirty:
            return True
        else:
            ret = Global._S3Connector.upload(key, self.data)
            if ret:
                self.dirty = False
                return True
            else:
                return False

    def read_block(self, block):
        if block.container_id != self.id:
            return None
        offset = block.offset
        if self.data[offset : offset + 20].hex() != block.block_id:
            return None
        offset += 20
        size = self.data[offset : offset + 2]
        size = size[0] * 256 + size[1]
        if size != block.size:
            return None
        offset += 2
        return self.data[offset : offset + size]

    def write_block(self, block_id, data):
        data_head = bytes.fromhex(block_id)
        size = len(data)
        data_size = six.int2byte(int(size / 256)) + six.int2byte(size % 256)
        data_to_write = data_head + data_size + data
        size += 22
        index = self.binary_search_in_fragments(size)
        if index is not None:
            fragment = self.fragments[index]
            self.fragments.remove(fragment)
            offset = fragment.offset
            self.data = self.data[0 : offset] + data_to_write + self.data[offset + size : len(self.data)]
            if fragment.size > size:
                fragment.offset += size
                fragment.size -= size
                self.add_fragment(fragment)
            self.dirty = True
            return Block(block_id, self.id, offset, size - 22)
        else:
            offset = len(self.data)
            if offset + size > Global.container_max_size:
                return None
            self.data = self.data + data_to_write
            self.dirty = True
            return Block(block_id, self.id, offset, size - 22)

    def delete_block(self, block):
        if block.container_id != self.id:
            return False
        offset = block.offset
        if self.data[offset : offset + 20].hex() != block.block_id:
            return False
        offset += 20
        size = self.data[offset : offset + 2]
        size = size[0] * 256 + size[1]
        if size != block.size:
            return False
        fragment = Fragment(block.offset, block.size + 22)
        self.add_fragment(fragment)
        fragments_size = 0
        for f in self.fragments:
            fragments_size += f.size
        if fragments_size * 2 > Global.container_max_size:
            self.defrag()
        else:
            self.data = self.data[0 : fragment.offset] + b'\x00' * fragment.size + self.data[fragment.offset + fragment.size : len(self.data)]
        self.dirty = True
        return True

    def defrag(self):
        self.quick_sort_fragments_by_offset()
        split = [0]
        for fragment in self.fragments:
            split.append(fragment.offset)
            split.append(fragment.offset + fragment.size)
        split.append(len(self.data))
        data = b''
        for i in range(0, len(split) / 2):
            data = data + self.data[split[2 * i] : split[2 * i + 1]]
        self.data = data
        #update mysql block index
        offset = 0
        length = len(self.data)
        while offset < length:
            block_id = self.data[offset : offset + 20].hex()
            size = self.data[offset + 20 : offset + 22]
            size = size[0] * 256 + size[1]
            Global._BlockIndex.update(Block(block_id, self.id, offset, size))
            offset += size + 22

    def add_fragment(self, fragment):
        index = self.binary_search_in_fragments(fragment.size)
        if index is None:
            self.fragments.append(fragment)
        else:
            self.fragments.insert(index, fragment)

    def binary_search_in_fragments(self, size):
        left = 0
        right = len(self.fragments) - 1
        if right < left:
            return None
        if self.fragments[right].size < size:
            return None
        while left < right:
            mid = int((left + right) / 2)
            if self.fragments[mid].size == size:
                return mid
            elif self.fragments[mid].size < size:
                left = mid + 1
            else:
                right = mid - 1
        if self.fragments[left].size < size:
            return left + 1
        else:
            return left

    def quick_sort_fragments_by_offset(self):
        quick_sort(self.fragments, 0, len(self.fragments) - 1)


class Fragment(Object):

    def __init__(self, offset, size):
        self.offset = offset
        self.size = size


def quick_sort(list, start, end):
    if start > end:
        return
    i, j = start, end
    flag = list[start]
    while True:
        while j > i and list[j].offset >= flag.offset:
            j -= 1
        while i < j and list[i].offset <= flag.offset:
            i += 1
        if i < j:
            list[i], list[j] = list[j], list[i]
        elif i == j:
            list[start], list[i] = list[i], list[start]
            break
    quick_sort(list,start, i - 1)
    quick_sort(list, i + 1, end)

def load(container_id):
    key = 'Container_' + str(container_id)
    data = Global._S3Connector.download(key)
    if data is None:
        return None
    container = Container(container_id)
    container.data = data
    container.dirty = False
    #initilize fragment information
    pos = 0
    length = len(container.data)
    while pos < length:
        index = container.data[pos : pos + 20]
        size = container.data[pos + 20 : pos + 22]
        size = size[0] * 256 + size[1]
        if index == b'\x00' * 20:
            container.add_fragment(Fragment(pos, size + 22))
        pos += size + 22
    return container