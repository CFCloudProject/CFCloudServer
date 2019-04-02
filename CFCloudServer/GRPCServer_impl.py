import sys
import json
import os
import math
import uuid
import operation_transform
import server_init
import utils
import vnode
import cdc
import config
import GRPCServer_pb2
import GRPCServer_pb2_grpc
import time


class GRPCServer_impl(GRPCServer_pb2_grpc.GRPCServerServicer):

    def Register(self, request, context):
        user = server_init._user_session.register(request.Email, request.Password, request.FirstName, request.LastName)
        if user is None:
            return GRPCServer_pb2.RegisterResult(Succeed = False, Error = 1)
        else:
            utils.create_user_namespace(user['user_id'])
            return GRPCServer_pb2.RegisterResult(Succeed = True, Error = 0)

    def Login(self, request, context):
        login_result = server_init._user_session.login(request.Email, request.Password)
        if login_result['code'] == 0:
            server_init._log = open(config.efs_root + '/' + login_result['session_id'] + '.log', 'w')
            return GRPCServer_pb2.LoginResult(
                Succeed = True, 
                SessionId = login_result['session_id'],
                FirstName = login_result['firstname'],
                LastName =  login_result['lastname'],
                Error = 0)
        else:
            return GRPCServer_pb2.LoginResult(
                Succeed = False, 
                SessionId = None,
                FirstName = None,
                LastName = None,
                Error = login_result['code'])

    def Logout(self, request, context):
        session_id = request.SessionId
        server_init._user_session.logout(session_id)
        server_init._log.flush()
        server_init._log.close()
        return GRPCServer_pb2.StringResponse(PayLoad = '')

    def Share(self, request, context):
        jstr = json.dumps({ 'error': 'share not developed'})
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def CreateFolder(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, request.Path)
        modified_time = request.ModifiedTime
        paths_to_create = []
        while not os.path.exists(truepath):
            paths_to_create.append(truepath)
            truepath = os.path.dirname(truepath)
        paths_to_create.reverse()
        for path in paths_to_create:
            os.mkdir(path)
            mnode = server_init._metadata_cache.get_usable_node(path + '/.metadata')
            mnode.acquire_lock()
            attrs = {}
            attrs['tag'] = 'folder'
            attrs['name'] = os.path.basename(path)
            fullname = path[len(config.efs_file_root) + 1:]
            fullname = fullname[fullname.find('/'):]
            attrs['fullname'] = fullname
            attrs['creation_time'] = modified_time
            attrs['owner'] = user
            attrs['shared_users'] = [user]
            attrs['is_shared'] = False
            attrs['is_deleted'] = False
            arguments = {}
            arguments['attributes'] = attrs
            arguments['path'] = path + '/.metadata'
            arguments['ottype'] = ''
            mnode.create(arguments)
            mnode.release_lock()
        truepath = truepath + '/.metadata'
        mnode = server_init._metadata_cache.get_usable_node(truepath)
        mnode.acquire_lock()
        if mnode.empty or not mnode.obj.path == truepath:
            mnode.load(truepath)
        jstr = json.dumps(mnode.obj.get_metadata())
        mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def Rename(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        path = request.OldPath
        newpath = request.Path
        user_root = config.efs_file_root + '/user_' + str(user['user_id'])
        pos = path.find('/', 1)
        if pos != -1:
            linkpath = user_root + path[:path.find('/', 1)] + '.li'
            if os.path.exists(linkpath):
                fp = open(path, 'r')
                per = fp.readline()
                fp.close()
                if pos != -1:
                    truepath = per + path[path.find('/', 1):]
                else:
                    truepath = per
            else:
                truepath = user_root + path
        else:
            linkpath = user_root + path + '.li'
            if os.path.exists(linkpath):
                os.rename(linkpath, user_root + newpath + '.li')
                truepath = None
            else:
                truepath = user_root + path
        if truepath is not None:
            if os.isdir(truepath):
                truepath = truepath + '/.metadata'
            else:
                truepath = truepath + '.metadata'
            mnode = server_init._metadata_cache.get_usable_node(truepath)
            mnode.acquire_lock()
            if mnode.empty or not mnode.obj.path == truepath:
                mnode.load(truepath)
            mnode.obj.set_attribute('name', os.path.basename(newpath))
            mnode.obj.set_attribute('fullpath', os.path.basename(newpath))
            mnode.release_lock()
            if os.isdir(truepath):
                truepath = truepath[:-10]
                os.rename(truepath, os.path.dirname(truepath) + '/' + os.path.basename(newpath))
            else:
                os.rename(truepath, os.path.dirname(truepath) + '/' + os.path.basename(newpath) + '.metadata')
        truepath = utils.get_true_path(user, request.Path) 
        if os.isdir(truepath):
            truepath = truepath + '/.metadata'
        else:
            truepath = truepath + '.metadata'
        mnode = server_init._metadata_cache.get_usable_node(truepath)
        mnode.acquire_lock()
        if mnode.empty or not mnode.obj.path == truepath:
            mnode.load(truepath)
        jstr = json.dumps(mnode.obj.get_metadata())
        mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def Delete(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, request.Path) 
        if os.isdir(truepath):
            truepath = truepath + '/.metadata'
        else:
            truepath = truepath + '.metadata'
        mnode = server_init._metadata_cache.get_usable_node(truepath)
        mnode.acquire_lock()
        if mnode.empty or not mnode.obj.path == truepath:
            mnode.load(truepath)
        mnode.obj.set_attribute('is_deleted', True)
        jstr = json.dumps(mnode.obj.get_metadata())
        mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def Upload(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, request.Path) + '.metadata'
        is_new = not server_init._metadata_cache.is_in_cache(truepath) and not os.path.exists(truepath)
        hashs = ''
        if not is_new:
            mnode = server_init._metadata_cache.get_usable_node(truepath)
            mnode.acquire_lock()
            if mnode.empty or not mnode.obj.path == truepath:
                mnode.load(truepath)
            base_hashs = mnode.obj.get_hashlist(request.BaseRev)
            mnode.release_lock()
        else:
            base_hashs = []
        for i in range(0, len(request.Hashs) / 20):
            _hash = request.Hashs[i*20:i*20+20]
            if not _hash in base_hashs and not server_init._hash_cache.search(_hash):
                hashs = hashs + _hash
        return GRPCServer_pb2.StringResponse(PayLoad = hashs)

    def UploadBlock(self, request_iterator, context):
        indexs = []
        hashs = []
        offsets = []
        datas = []
        _offset = 0
        for request in request_iterator:
            session_id = request.SessionId
            path = request.Path
            modified_time = request.ModifiedTime
            base_rev = request.BaseRev
            ottype = request.OtType
            indexs.append(request.Index)
            hashs.append(request.Hash)
            datas.append(request.Content)
            offsets.append(_offset)
            _offset += request.Size
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, path) + '.metadata'
        is_new = not server_init._metadata_cache.is_in_cache(truepath) and not os.path.exists(truepath)
        if is_new:
            psid = server_init._psi.get_psid_by_filepath(truepath[:-9])
            if psid is None:
                container_id = utils.get_new_container_id()
                cnode = server_init._container_cache.get_usable_node(container_id)
                cnode.acquire_lock()
                cnode.create(container_id)
                cnode.release_lock()
                psid = str(uuid.uuid1())
                pnode = server_init._psi_cache.get_usable_node(psid)
                pnode.acquire_lock()
                pnode.create({
                    'type': 'c',
                    'id': psid,
                    'paths': [truepath[:-9]], 
                    'container_ids': [container_id]
                    })
            else:
                pnode = server_init._psi_cache.get_usable_node(psid)
                pnode.acquire_lock()
                if pnode.empty or not pnode.obj.id == psid:
                    pnode.load(psid)
            for i in range(0, len(hashs)):
                if not server_init._hash_cache.search(hashs[i]):
                    r_psid = pnode.obj.write_block(truepath[:-9], hashs[i], datas[i])
                    if not r_psid == psid:
                        pnode.release_lock()
                        psid = r_psid
                        pnode = server_init._psi_cache.get_usable_node(psid)
                        pnode.acquire_lock()
                        if pnode.empty or not pnode.obj.id == psid:
                            pnode.load(psid)
            pnode.release_lock()
            mnode = server_init._metadata_cache.get_usable_node(truepath)
            mnode.acquire_lock()
            attrs = {}
            attrs['tag'] = 'file'
            attrs['name'] = os.path.basename(path)
            attrs['fullname'] = path
            attrs['creation_time'] = modified_time
            attrs['owner'] = user
            attrs['shared_users'] = [user]
            attrs['is_shared'] = False
            attrs['is_deleted'] = False
            arguments = {}
            arguments['attributes'] = attrs
            arguments['path'] = truepath
            arguments['ottype'] = ottype
            mnode.create(arguments)
            _nodeattrs = {}
            _nodeattrs['size'] = _offset
            _nodeattrs['op_size'] = 0
            _nodeattrs['base_rev'] = -1
            _nodeattrs['modifier'] = user
            _nodeattrs['modified_time'] = modified_time
            _node = vnode.vnode(_nodeattrs, True, hashs, None)
            mnode.obj.add_vnode(_node)
            retstr = json.dumps(mnode.obj.get_metadata())
            mnode.release_lock()
            server_init._log.write('0\n')
        else:
            mnode = server_init._metadata_cache.get_usable_node(truepath)
            mnode.acquire_lock()
            if mnode.empty or not mnode.obj.path == truepath:
                mnode.load(truepath)
            if mnode.obj.is_deleted:
                mnode.obj.is_deleted = False
                if base_rev is None:
                    base_rev = mnode.obj.get_attribute['rev']
            is_checkpoint = mnode.obj.versions.next_is_checkpoint()
            data_base = mnode.obj.read(base_rev)
            offsets_base = mnode.obj.get_offsets(base_rev)
            hashs_base = mnode.obj.get_hashlist(base_rev)
            data_new = b''
            for i in range(0, len(hashs)):
                if datas[i] is None:
                    if hashs[i] in hashs_base:
                        _i = hashs_base.index(hashs[i])
                        datas[i] = data_base[offsets_base[_i]:offsets_base[_i+1]]
                    else:
                        block = server_init._block_index.select(hashs[i])
                        cnode = server_init._container_cache.get_usable_node(block['container_id'])
                        cnode.acquire_lock()
                        if cnode.empty or not cnode.obj.id == block['container_id']:
                            cnode.load(block['container_id'])
                        datas[i] = cnode.obj.read_block(block)
                        cnode.release_lock()
                data_new = data_new + datas[i]
            if not is_checkpoint:
                ot_start = time.time() * 1000
                ot = operation_transform.operation_transform(mnode.obj.versions.optype)
                oplist = ot.generate_oplist(data_base, data_new)
                op_data = ot.oplist2bytes(oplist)
                opsize = len(op_data)
                ot_end = time.time() * 1000
                server_init._log.write(str(ot_end - ot_start) + '\n')
                if opsize >= _offset:
                    is_checkpoint = True
                else:
                    ops = []
                    chunker = cdc.cdc(op_data)
                    chunker.chunking()
                    data_to_store = []
                    for chunk in chunker.getchunks():
                        data_to_store.append(chunk['data'])
                        ops.append(chunk['hash'])
                    hash_to_store = ops
            else:
                opsize = 0
                ops = None
                server_init._log.write('0\n')
            if is_checkpoint:
                hash_to_store = hashs
                data_to_store = datas
            psid = server_init._psi.get_psid_by_filepath(truepath[:-9])
            pnode = server_init._psi_cache.get_usable_node(psid)
            pnode.acquire_lock()
            if pnode.empty or not pnode.obj.id == psid:
                pnode.load(psid)
            for i in range(0, len(hash_to_store)):
                if not server_init._hash_cache.search(hash_to_store[i]):
                    r_psid = pnode.obj.write_block(truepath[:-9], hash_to_store[i], data_to_store[i])
                    if not r_psid == psid:
                        pnode.release_lock()
                        psid = r_psid
                        pnode = server_init._psi_cache.get_usable_node(psid)
                        pnode.acquire_lock()
                        if pnode.empty or not pnode.obj.id == psid:
                            pnode.load(psid)
            pnode.release_lock()
            _node = vnode.vnode({}, is_checkpoint, hashs, offsets, ops)
            _node.set_attribute('size', _offset)
            _node.set_attribute('opsize', opsize)
            _node.set_attribute('base_rev', base_rev)
            _node.set_attribute('modifier', user)
            _node.set_attribute('modified_time', modified_time)
            _mnode.obj.add_vnode(_node)
            retstr = json.dumps(mnode.obj.get_metadata())
            mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = retstr)

    def Download(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, request.Path) + '.metadata'
        mnode = server_init._metadata_cache.get_usable_node(truepath)
        mnode.acquire_lock()
        if mnode.empty or not mnode.obj.path == truepath:
            mnode.load(truepath)
        hashs = mnode.obj.get_hashlist()
        rev = mnode.obj.get_attribute('rev')
        jstr = json.dumps({ 'rev': rev, 'hashs': hashs })
        mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def DownloadBlock(self, request_iterator, context):
        hashs = []
        for request in request_iterator:
            session_id = request.SessionId
            path = request.Path
            base_rev = request.BaseRev
            hashs.append(request.Hash)
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, path) + '.metadata'
        mnode = server_init._metadata_cache.get_usable_node(truepath)
        mnode.acquire_lock()
        if mnode.empty or not mnode.obj.path == truepath:
            mnode.load(truepath)
        data = mnode.obj.read(base_rev)
        hashs_base = mnode.obj.get_hashlist(base_rev)
        offsets_base = mnode.obj.get_offsets(base_rev)
        blocks = []
        for hash in hashs:
            i = hashs_base.index(hash)
            blockdata = data[offsets_base[i]:offsets_base[i+1]]
            blocks.append({ 'hash': hash, 'data': blockdata.hex() })
        jstr = json.dumps({ 'blocks': blocks })
        mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def GetMetadata(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, request.Path) 
        if os.isdir(truepath):
            truepath = truepath + '/.metadata'
        else:
            truepath = truepath + '.metadata'
        mnode = server_init._metadata_cache.get_usable_node(truepath)
        mnode.acquire_lock()
        if mnode.empty or not mnode.obj.path == truepath:
            mnode.load(truepath)
        jstr = json.dumps(mnode.obj.get_metadata())
        mnode.release_lock()
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def ListFolder(self, request, context):
        session_id = request.SessionId
        user = server_init._user_session.get_user_by_session(session_id)
        truepath = utils.get_true_path(user, request.Path)
        metadatas = []
        for child in os.listdir(truepath):
            if child == '.metadata':
                continue
            elif child.endswith('.metadata'):
                meta_path = '/'.join([truepath, child])
            else:
                meta_path = '/'.join([truepath, child, '.metadata'])
            mnode = server_init._metadata_cache.get_usable_node(meta_path)
            mnode.acquire_lock()
            if mnode.empty or not mnode.obj.path == meta_path:
                mnode.load(meta_path)
            metadatas.append(mnode.obj.get_metadata())
            mnode.release_lock()
        jstr = json.dumps({ 'entries': metadatas })
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)
