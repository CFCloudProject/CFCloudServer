import threading

class cnode(object):
    __slots__ = ('empty', 'next', 'prev', 'name', 'key', 'obj', 'lock')

    def __init__(self, name):
        self.name = name
        self.empty = True
        self.obj = None
        self.lock = threading.Lock()

    def acquire_lock(self):
        self.lock.acquire()

    def release_lock(self):
        self.lock.release()

    def load(self, arg):
        if not self.empty:
            self.obj.write_back()
        self.obj = __import__(self.name).load(arg)
        self.empty = False

    def create(self, arg = None):
        if not self.empty:
            self.obj.write_back()
        if key is None:
            self.obj = __import__(self.name).create()
        else:
            self.obj = __import__(self.name).create(arg)
        self.empty = False

class cache(object):

    def __init__(self, max, name):
        self.max = max
        self.name = name
        self.lock = threading.Lock()
        self.table = {}
        self.count = 0
        self.head = cnode(name)
        _iter = self.head
        for i in range(0, max - 1):
            iter = cnode(name)
            iter.prev = _iter
            _iter.next = iter
            _iter = iter
        _iter.next = self.head
        self.head.prev = _iter

    def __visit(self, _node):
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

    def get_usable_node(self, key):
        self.lock.acquire()
        node = table.get(key)
        if node is None:
            if self.count == self.max:
                node = self.head.prev
                self.table.pop(node.key)
            else:
                node = self.head
                while not node.empty:
                    node = node.next
                self.count += 1
            self.table[key] = node
        node.key = key
        self.__visit(node)
        node.acquire_lock()
        self.lock.release()
        return node
