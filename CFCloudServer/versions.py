import vnode
import operation_transform
import cdc
import config
import time

class versions(object):
    
    def __init__(self, optype):
        self.optype = optype
        self.rev = -1
        self.checkpoints = []
        self.vector = []

    def get_rev_metadata(self, rev = None):
        if rev is None:
            rev = self.rev
        return self.vector[rev].get_metadata()

    def get_hashlist(self, rev = None):
        if rev is None:
            rev = self.rev
        return self.vector[rev].get_hastlist()

    def get_offsets(self, rev = None):
        if rev is None:
            rev = self.rev
        return self.vector[rev].get_offsets()

    def get_size_hashs(self):
        size = 0
        hashs = []
        for version in self.vector:
            (_size, _hashs) = version.get_size_hashs()
            size += _size
            hashs.extend(_hashs)
        return { 'size': size, 'hashs': hashs }

    def add_vnode(self, node, ignore = False):
        if node.get_attribute('base_rev') < self.rev:
            conflict = True
        self.rev += 1
        node.set_attribute('rev', self.rev)
        if node.is_checkpoint:
            self.checkpoints.append(self.rev)
        self.vector.append(node)
        if not ignore and conflict:
            (hashs, datas) = self.resolve_conflict()
            return hashs, datas
        return None, None

    def resolve_conflict(self):
        base = self.find_same_base(self.rev, self.rev - 1)
        opleft = b''
        r = self.rev - 1
        while not r == base:
            opleft = self.vector[r].read() + opleft
            rev = self.vector[r].get_attribute('base_rev')
        opright = b''
        r = self.rev
        while not r == base:
            opright = self.vector[r].read() + opright
            rev = self.vector[r].get_attribute('base_rev')
        ot = operation_transform.operation_transform(self.optype)
        op = ot.transform_oplist_oplist(ot.bytes2oplist(opleft), ot.bytes2oplist(opright))
        op_data = ot.oplist2bytes(op)
        base_data = self.read(base)
        if self.optype == 's':
            base_data = base_data.decode()
        data = ot.execute_oplist(base_data, op)
        if self.optype == 's':
            data = data.encode()
        hashs = []
        offsets = []
        chunker = cdc.cdc(data)
        chunker.chunking()
        for chunk in chunker.getchunks():
            hashs.append(chunk['hash'])
            offsets.append(chunk['start'])
        ops = []
        chunker = cdc.cdc(op_data)
        chunker.chunking()
        data_to_store = []
        for chunk in chunker.getchunks():
            data_to_store.append(chunk['data'])
            ops.append(chunk['hash'])
        node = vnode.vnode({}, False, hashs, offsets, ops)
        node.set_attribute('size', len(data))
        node.set_attribute('opsize', len(op_data))
        node.set_attribute('base_rev', self.rev - 1)
        node.set_attribute('modifier', config.server_user)
        node.set_attribute('modified_time', int(time.time() * 1000))
        self.add_vnode(node, True)
        return ops, data_to_store

    def find_same_base(self, v1, v2):
        if v1 == v2:
            return v1
        elif v1 < v2:
            return self.find_same_base(v1, self.vector[v2].get_attribute('base_rev'))
        else:
            return self.find_same_base(v2, self.vector[v1].get_attribute('base_rev'))

    def read(self, rev = None):
        if rev is None:
            rev = self.rev
        op = b''
        while not rev in self.checkpoints:
            op = self.vector[rev].read() + op
            rev = self.vector[rev].get_attribute('base_rev')
        base = self.vector[rev].read()
        if not op == b'':
            ot = operation_transform.operation_transform(self.optype)
            if self.optype == 's':
                base = base.decode()
                return ot.execute_oplist(base, ot.bytes2oplist(op)).encode()
            else:
                return ot.execute_oplist(base, ot.bytes2oplist(op))
        else:
            return base

    def next_is_checkpoint(self):
        return self.rev - self.checkpoints[len(self.checkpoints) - 1] > 4

    def to_dict(self):
        dict = {}
        dict['optype'] = self.optype
        dict['rev'] = self.rev
        dict['checkpoints'] = self.checkpoints
        dict['vector'] = []
        for _vnode in self.vector:
            dict['vector'].append(_vnode.__dict__)
        return dict

def from_dict(dict):
    _versions = versions()
    _versions.optype = dict.get('optype')
    _versions.rev = dict.get('rev')
    _versions.checkpoints = dict.get('checkpoints')
    vector = dict.get('vector')
    for v_dict in vector:
        _versions.vector.append(vnode.from_dict(v_dict))
    return _versions