import re
import six
from . import diff_match_patch, Operation

# operation generation
# old & new must be bytes
def GenerateOpList(old, new):
    dmp = diff_match_patch.diff_match_patch()
    diffs = dmp.diff_main(old.hex(), new.hex())
    dmp.diff_cleanupEfficiency(diffs)
    index = 0
    ret = []
    for diff in diffs:
        if diff[0] == 0:
            index = index + len(diff[1])
        elif diff[0] == 1:
            ret.append(Operation.Operation('i', index, diff[1]))
            index = index + len(diff[1])
        else:
            ret.append(Operation.Operation('d', index, len(diff[1])))
    return ret

# transform function
def TransformOpvsOp(o1, o2):
    if o1.type == 'i' and o2.type == 'i':
        if o1.index <= o2.index:
            o2.index = o2.index + len(o1.data)
        return o2, None
    elif o1.type == 'i' and o2.type == 'd':
        if o1.index <= o2.index:
            o2.index = o2.index + len(o1.data)
            return o2, None
        elif o2.index < o1.index < o2.index + o2.data:
            length = o2.data
            o2.data = o1.index - o2.index
            return o2, Operation.Operation('d', o2.index + len(o1.data), o2.index + length - o1.index)
        else:
            return o2, None
    elif o1.type == 'd' and o2.type == 'i':
        if o1.index + o1.data < o2.index:
            o2.index = o2.index - o1.data
            return o2, None
        elif o1.index < o2.index < o1.index + o1.data:
            o2.index = o1.index
            return o2, None
        else:
            return o2, None
    else:
        if o1.index + o1.data <= o2.index:
            o2.index = o2.index - o1.data
            return o2, None
        elif o1.index <= o2.index < o1.index + o1.data:
            o2.index = o1.index
            o2.data = o2.index - o1.index + o2.data - o1.data
            if o2.data <= 0:
                return None, None
            return o2, None
        elif o2.index < o1.index < o2.index + o2.data:
            after = o2.index + o2.data - o1.index - o1.data
            if after < 0:
                after = 0
            o2.data = o1.index - o2.index + after
            return o2, None
        else:
            return o2, None

def BackforwardOpvsOp(o1, o2):
    if o1.type == 'i':
        if o1.index < o2.index:
            o2.index = o2.index - len(o1.data)
    elif o1.type == 'd':
        if o1.index < o2.index:
            o2.index = o2.index + o1.data
    return o2

def BackforwardOpList(l):
    if len(l) <= 1:
        return l
    ret = []
    ret.append(l.pop())
    while len(l) > 0:
        tmp = []
        o = l.pop()
        tmp.append(o)
        for op in ret:
            tmp.append(BackforwardOpvsOp(o, op))
        ret = tmp
    return ret

def TransformOpvsOpList(op, l):
    ret = []
    if len(l) == 0:
        return ret
    for o in l:
        o1, o2 = TransformOpvsOp(op, o)
        if o1 is not None:
            ret.append(o1)
        if o2 is not None:
            ret.append(o2)
    return ret

def TransformOpListvsOpList(l1, l2):
    l2 = BackforwardOpList(l2)
    for o in l1:
        l2 = TransformOpvsOpList(o, l2)
    while len(l2) > 0:
        o = l2[0]
        l2 = l2[1:len(l2)]
        l2 = TransformOpvsOpList(o, l2)
        l1.append(o)
    return l1

# execute operation
# b must be bytes
def ExecuteOp(b, o):
    s = b.hex()
    if o.type == 'i':
        ret = s[:o.index] + o.data + s[o.index:len(s)]
    else:
        ret = s[:o.index] + s[o.index + o.data:len(s)]
    return bytes.fromhex(ret)

# b must be bytes
def ExecuteOpList(b, l):
    for o in l:
        b = ExecuteOp(b, o)
    return b

# convert between oplist and bytes
def oplist2bytes(l):
    ret = b''
    for op in l:
        b_op = op.op2bytes()
        len = len(b_op)
        ret += six.int2byte(int(len / 256)) + six.int2byte(len % 256) + b_op
    return ret

def bytes2oplist(b):
    pos = 0
    len = len(b)
    oplist = []
    while pos < len:
        op_len = b[pos] * 256 + b[pos + 1]
        pos += 2
        oplist.append(Operation.bytes2op(b[pos : pos + op_len]))
        pos += op_len
    return oplist