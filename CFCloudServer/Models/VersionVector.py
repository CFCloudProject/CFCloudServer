class VersionVector(object):
    
    def __init__(self):
        self.version = 0
        self.vector = []

    def add(self, vnode):
        self.version += 1
        self.vector.append(vnode)

    def read_data(self, version, block_index):
        return self.vector[version].read_data(block_index)


