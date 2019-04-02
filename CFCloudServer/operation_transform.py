import re
import six
import utils
import diff_match_patch

class operation(object):

    def __init__(self, type, index, data):
        self.type = type
        self.index = index
        self.data = data

    def op2bytes(self, mode):
        b_type = self.type.encode()
        b_index = utils.int2bytes(self.index)
        b_index = six.int2byte(len(b_index)) + b_index
        if self.type == 'i':
            b_data = self.data.encode()
        else:
            b_data = utils.int2bytes(self.data)
        return b_type + b_index + b_data

    def bytes2op(b, mode):
        type = chr(b[0])
        length = b[1]
        index = utils.bytes2int(b[2:length+2])
        if type == 'i':
            data = b[length+2:].decode()
        else:
            data = utils.bytes2int(b[length+2:])
        return operation(type, index, data)

class operation_transform(object):

    def __init__(self, mode):
        self.mode = mode

    # operation generation
    def generate_oplist(self, old, new):
        dmp = diff_match_patch.diff_match_patch()
        if self.mode == 'b':
            diffs = dmp.diff_main(old.hex(), new.hex())
        else:
            diffs = dmp.diff_main(old, new)
        dmp.diff_cleanupEfficiency(diffs)
        index = 0
        ret = []
        for diff in diffs:
            if diff[0] == 0:
                index += len(diff[1])
            elif diff[0] == 1:
                ret.append(operation('i', index, diff[1]))
                index += len(diff[1])
            else:
                ret.append(operation('d', index, len(diff[1])))
        return ret

    # transform function
    def transform_oplist_oplist(l1, l2):

        def transform_op_op(o1, o2):
            if o1.__dict__ == o2.__dict__:
                return None, None
            if o1.type == 'i' and o2.type == 'i':
                if o1.index <= o2.index:
                    o2.index += len(o1.data)
                return o2, None
            elif o1.type == 'i' and o2.type == 'd':
                if o1.index <= o2.index:
                    o2.index += len(o1.data)
                    return o2, None
                elif o2.index < o1.index < o2.index + o2.data:
                    length = o2.data
                    o2.data = o1.index - o2.index
                    return o2, operation('d', o2.index + len(o1.data), o2.index + length - o1.index)
                else:
                    return o2, None
            elif o1.type == 'd' and o2.type == 'i':
                if o1.index + o1.data < o2.index:
                    o2.index -= o1.data
                elif o1.index < o2.index < o1.index + o1.data:
                    o2.index = o1.index
                else:
                    pass
                return o2, None
            else:
                if o1.index + o1.data <= o2.index:
                    o2.index -= o1.data
                elif o1.index <= o2.index < o1.index + o1.data:
                    o2.index = o1.index
                    o2.data = o2.index - o1.index + o2.data - o1.data
                    if o2.data <= 0:
                        return None, None
                elif o2.index < o1.index < o2.index + o2.data:
                    after = o2.index + o2.data - o1.index - o1.data
                    if after < 0:
                        after = 0
                    o2.data = o1.index - o2.index + after
                else:
                    pass
                return o2, None

        def backforward_op_op(o1, o2):
            if o1.type == 'i':
                if o1.index < o2.index:
                    o2.index -= len(o1.data)
            elif o1.type == 'd':
                if o1.index < o2.index:
                    o2.index += o1.data
            return o2

        def backforward_oplist(l):
            if len(l) <= 1:
                return l
            ret = []
            ret.append(l.pop())
            while len(l) > 0:
                tmp = []
                o = l.pop()
                tmp.append(o)
                for op in ret:
                    tmp.append(backforward_op_op(o, op))
                ret = tmp
            return ret

        def transform_op_oplist(op, l):
            ret = []
            if len(l) == 0:
                return ret
            for o in l:
                (o1, o2) = transform_op_op(op, o)
                if o1 is not None:
                    ret.append(o1)
                if o2 is not None:
                    ret.append(o2)
            return ret

        l2 = backforward_oplist(l2)
        for o in l1:
            l2 = transform_op_oplist(o, l2)
        l3 = []
        while len(l2) > 0:
            o = l2[0]
            l2 = l2[1:]
            l2 = transform_op_oplist(o, l2)
            l3.append(o)
        return l3

    # execute operation
    def execute_oplist(self, b, l):

        def execute_op(b, o):
            if self.mode == 'b':
                s = b.hex()
            else:
                s = b

            if o.type == 'i':
                ret = s[:o.index] + o.data + s[o.index:]
            else:
                ret = s[:o.index] + s[o.index + o.data:]

            if self.mode == 'b':
                return bytes.fromhex(ret)
            else:
                return ret

        for o in l:
            b = execute_op(b, o)
        return b

    # convert between oplist and bytes
    def oplist2bytes(self, l):
        ret = b''
        for op in l:
            b_op = op.op2bytes(self.mode)
            length = len(b_op)
            b_length = utils.int2bytes(length)
            ret += six.int2byte(length) + b_length + b_op
        return ret

    def bytes2oplist(self, b):
        pos = 0
        length = len(b)
        oplist = []
        while pos < length:
            ll = b[pos]
            pos += 1
            op_len = utils.bytes2int(b[pos:pos+ll])
            pos += ll
            oplist.append(operation.bytes2op(b[pos : pos + op_len], self.mode))
            pos += op_len
        return oplist
