import six

# define operation
class Operation(object):

    def __init__(self, type, index, data):
        self.type = type
        self.index = index
        self.data = data

    def op2bytes(self):
        b_type = self.type.encode()
        b_index = six.int2byte(int(self.index / 256)) + six.int2byte(self.index % 256)
        if self.type == 'i':
            b_data = bytes.fromhex(self.data)
        else:
            b_data = six.int2byte(int(self.data / 256)) + six.int2byte(self.data % 256)
        return b_type + b_index + b_data

def bytes2op(b):
    type = b[0].decode()
    index = b[1] * 256 + b[2]
    if type == 'i':
        data = b[3 : len(b)].hex()
    else:
        data = b[3] * 256 + b[4]
    return Operation(type, index, data)