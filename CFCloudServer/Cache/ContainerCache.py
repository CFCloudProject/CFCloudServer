import Models.Container as Container
import threading

class ccnode(object):
    __slots__ = ('empty', 'next', 'prev', 'container', 'lock')

    def __init__(self):
        self.empty = True
        self.lock = threading.Lock()

    def read_block(self, block):
        self.lock.acquire()
        if block.container_id != self.container.id:
            self.load_container(block.container_id)
        ret = self.container.read_block(block)
        self.lock.release()
        return ret

    def write_block(self, container_id, block_id, data):
        self.lock.acquire()
        if container_id != self.container.id:
            self.__load_container(container_id)
        ret = self.container.write_block(block_id, data)
        self.lock.release()
        return ret

    def delete_block(self, block):
        self.lock.acquire()
        if block.container_id != self.container.id:
            self.load_container(block.container_id)
        ret = self.container.delete_block(block)
        self.lock.release()
        return ret

    def __load_container(self, container_id):
        if not self.empty:
            write_back = False
            while not write_back:
                write_back = self.container.write_back()
        self.container = None
        while self.container is None:
            self.container = Container.load(container_id)
        self.empty = False


class ContainerCache(object):

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

    def __get_usable_node(self, container_id):
        self.lock.acquire()
        node = table.get(container_id)
        if node is None:
            if self.count == self.max:
                node = self.head.prev
                self.table.pop(node.container.id)
            else:
                node = self.head
                while not node.empty:
                    node = node.next
                self.count += 1
            self.table[container_id] = node
        self.__visit(node)
        self.lock.release()
        return node

    def read_block(self, block):
        node = self.__get_usable_node(block.container_id)
        return node.read_block(block)

    def write_block(self, container_id, block_id, data):
        node = self.__get_usable_node(container_id)
        return node.write_block(container_id, block_id, data)

    def delete_block(self, block):
        node = self.__get_usable_node(block.container_id)
        return node.delete_block(block)

