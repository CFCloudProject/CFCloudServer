class VitrualBlock(object):
    
    def __init__(self, base=None, op=None, current=None, sha256=None, md5=None):
        self.base = base
        self.op = op
        self.current = current
        self.sha256 = sha256
        self.md5 = md5

    def read_data(self):
        if self.current is not None:
            pass
        else:
            pass


