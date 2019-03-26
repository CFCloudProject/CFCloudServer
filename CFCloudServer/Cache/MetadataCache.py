import threading
import Models.Metadata as Metadata

class mcnode(object):
    __slots__ = ('empty', 'next', 'prev', 'metadata', 'lock')

    def __init__(self):
        self.empty = True
        self.metadata = None
        self.lock = threading.Lock()

    def __load_metadata(self, path):
        if not self.empty:
            self.metadata.write_back()
        self.metadata = Metadata.load(path)
        self.empty = False

    def get_attribute(self, path, name):
        self.lock.acquire()
        if self.metadata.meta_path != path:
            self.__load_metadata(path)
        attr = self.metadata.get_attribute(name)
        self.lock.release()
        return attr

    def set_attribute(self, path, name, attr):
        self.lock.acquire()
        if self.metadata.meta_path != path:
            self.__load_metadata(path)
        self.metadata.set_attribute(name, attr)
        self.lock.release()

    def create_temp_version(self, path, fullpath, modifier, modified_time, size, base_rev):
        self.lock.acquire()
        if base_rev is None:
            if not self.empty:
                self.metadata.write_back()
            self.metadata = Metadata.Metadata('File', fullpath[fullpath.rfind('/') + 1 : len(fullpath)], 
                                              fullpath, size, -1, modified_time, modified_time, 
                                              modifier, modifier, False, [modifier])
        elif self.metadata.meta_path != path:
            self.__load_metadata(path)
        rev, hashlist = self.metadata.create_temp_version(modifier, modified_time, size, base_rev)
        self.lock.acquire()
        return rev, hashlist

    def add_vitrual_block(self, path, rev, block):
        self.lock.acquire()
        if self.metadata.meta_path != path:
            self.__load_metadata(path)
        self.metadata.add_vitrual_block(rev, block)
        self.lock.release()

    def read_block(self, path, rev, index):
        self.lock.acquire()
        if self.metadata.meta_path != path:
            self.__load_metadata(path)
        data = self.metadata.read_block(rev, index)
        self.lock.release()
        return data

    def read_blocks(self, path, rev, indexs):
        self.lock.acquire()
        if self.metadata.meta_path != path:
            self.__load_metadata(path)
        data = self.metadata.read_blocks(rev, indexs)
        self.lock.release()
        return data

    def set_readable(self, path, rev):
        self.lock.acquire()
        if self.metadata.meta_path != path:
            self.__load_metadata(path)
        self.metadata.set_readable(rev)
        self.lock.release()

class MetadataCache(object):

    def __init__(self, max_cache):
        self.max = max_cache
        self.lock = threading.RLock()
        self.table = {}
        self.count = 0
        self.head = ccnode()
        _iter = self.head
        for i in range(0, max_cache - 1):
            iter = ccnode()
            iter.prev = _iter
            _iter.next = iter
            _iter = iter
        _iter.next = self.head
        self.head.prev = _iter

    def __visit(self, _node):
        self.lock.acquire()
        if _node == self.head:
            pass
        elif _node == self.head.prev:
            self.head = _node
        else:
            _node.prev.next = _node.next
            _node.next.prev = _node.prev
            _node.next = self.head
            _node.prev = self.head.prev
            self.head.prev.next = _node
            self.head.prev = _node
            self.head = _node
        self.lock.release()

    def __get_usable_node(self, path):
        self.lock.acquire()
        node = table.get(path)
        if node is None:
            if self.count == self.max:
                node = self.head.prev
                self.table.pop(node.metadata.meta_path)
            else:
                node = self.head
                while not node.empty:
                    node = node.next
                self.count += 1
            self.table[path] = node
        self.__visit(node)
        self.lock.release()
        return node

    def get_attribute(self, path, name):
        node = self.__get_usable_node(path)
        return node.get_attribute(path, name)

    def set_attribute(self, path, name, attr):
        node = self.__get_usable_node(path)
        return node.set_attribute(path, name, attr)

    def create_temp_version(self, path, fullpath, modifier, modified_time, size, base_rev):
        node = self.__get_usable_node(path)
        rev, hashlist = node.create_temp_version(path, fullpath, modifier, modified_time, size, base_rev)
        return rev, hashlist

    def add_vitrual_block(self, path, rev, block):
        node = self.__get_usable_node(path)
        node.add_vitrual_block(path, rev, block)

    def read_block(self, path, rev, index):
        node = self.__get_usable_node(path)
        return node.read_block(path, rev, index)

    def read_blocks(self, path, rev, indexs):
        node = self.__get_usable_node(path)
        return node.read_block(path, rev, indexs)

    def set_readable(self, path, rev):
        node = self.__get_usable_node(path)
        node.set_readable(path, rev)