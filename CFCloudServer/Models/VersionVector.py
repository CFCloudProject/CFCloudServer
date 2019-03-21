class VersionVector(object):
    
    def __init__(self):
        self.version = 0
        self.vector = []

    def add(self, vnode):
        self.version += 1
        self.vector.append(vnode)


