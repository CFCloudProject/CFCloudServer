import threading
import Models.Metadata as Metadata

class mcnode(object):
    __slots__ = ('empty', 'next', 'prev', 'metadata', 'lock')

    def __init__(self):
        self.empty = True
        self.lock = threading.Lock()

    def __load_metadata(self, path):
        if not self.empty:
            self.metadata.write_back()
        self.metadata = Metadata.load(path)
        self.empty = False

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