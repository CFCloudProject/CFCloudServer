import sys
import json
import math
import Global
from . import GRPCServer_pb2, GRPCServer_pb2_grpc


class GRPCServerImpl(GRPCServer_pb2_grpc.GRPCServerServicer):

    def Register(self, request, context):
        user = Global._user_cache.register(request.Email, request.Password, request.FirstName, request.LastName)
        if user is None:
            return GRPCServer_pb2.RegisterResult(Succeed = False, Error = 1)
        else:
            Global.create_user_namespace(user.userid)
            return GRPCServer_pb2.RegisterResult(Succeed = True, Error = 0)

    def Login(self, request, context):
        email = request.Email
        password = request.Password
        flag, session_id, firstname, lastname = Global._user_cache.login(email, password)
        if flag == 0:
            return GRPCServer_pb2.LoginResult(
                Succeed = True, 
                Error = 0, 
                Email = email, 
                FirstName = firstname, 
                LastName = lastname)
        elif flag == 1:
            return GRPCServer_pb2.LoginResult(
                Succeed = False, 
                Error = 1, 
                SessionId = None,
                Email = None, 
                FirstName = None,
                LastName = None)
        else:
            return GRPCServer_pb2.LoginResult(
                Succeed = False, 
                Error = 2, 
                SessionId = None,
                Email = None, 
                FirstName = None,
                LastName = None)

    def Logout(self, request, context):
        session_id = request.SessionId
        Global._user_cache.logout(session_id)
        return GRPCServer_pb2.StringResponse(PayLoad = '')

    def HeartBeat(self, request, context):
        return super().HeartBeat(request, context)

    def Share(self, request, context):
        return super().Share(request, context)

    def CreateFolder(self, request, context):
        return super().CreateFolder(request, context)

    def Rename(self, request, context):
        return super().Rename(request, context)

    def Delete(self, request, context):
        return super().Delete(request, context)

    def Upload(self, request, context):
        user_id = connect_user.get(request.SessionId)
        basefile = request.BaseRev 
        path = request.Path
        size = request.Size
        time = request.Time
        metadata = Metadata()
        if(metadata.readMetadata(path)==False):
            metadata.vv.size = size
            metadata.vv.time = time
            metadata.writeMetadata(path)
        version_num = metadata.vv.version + 1
        if(basefile == None):
            jstr = json.dumps(blockInfo(version_num,[]))
            return GRPCServer_pb2.StringResponse(PayLoad = jstr)
        else:
            infos = []
            for block in metadata.vv[int(basefile)].blocks:
                infos.append((block.sha256,block.md5s))
            jstr = json.dumps(blockInfo(version_num,infos))
            return GRPCServer_pb2.StringResponse(PayLoad = jstr)
        #return super().Upload(request, context)

    def UploadBlock(self, request_iterator, context):
        vblockList = []
        path = request_iterator.path
        while(1):
            size = request_iterator.size  
            container, containid, unitid = recAddNode(root, path, 0, size)
            bid = container.writeContainer(unitid, request_iterator.data, size)
            block = Block(bid, containid, unitid, math.ceil(size/UNITSIZE), size)
            insert(block)
            vblockList.append(block)
            yield model_pb2.file_Response(data = block)
        # wait for further 
        vnode = VersionNode(request_iterator.verNum, vblockList)
        #return super().UploadBlock(request_iterator, context)

    def Download(self, request, context):
        return super().Download(request, context)

    def DownloadBlock(self, request_iterator, context):
        return super().DownloadBlock(request_iterator, context)

    def GetMetadata(self, request, context):
        return super().GetMetadata(request, context)

    def ListFolder(self, request, context):
        return super().ListFolder(request, context)
