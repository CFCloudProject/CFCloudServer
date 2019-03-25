import sys
import json
import math
import Global
import GRPCServer_pb2
import GRPCServer_pb2_grpc


class GRPCServerImpl(GRPCServer_pb2_grpc.GRPCServerServicer):

    def Register(self, request, context):
        email = request.Email
        password = request.Password
        db_password = account_dic.get(email, None)
        if(db_password==None):
            user_id = createUserFold()
            writeShadow(email, password, user_id, request.FirstName, request.LastName, account_dic)            
            return GRPCServer_pb2.RegisterResult(Succeed  = True, Error = 0)
        else:
            return GRPCServer_pb2.RegisterResult(Succeed  = False, Error = 1)
        #return super().Register(request, context)

    def Login(self, request, context):
        email = request.Email
        password = request.Password
        info = account_dic.get(email, None)
        db_password = info[0]
        user_id = info[1]
        if(db_password==None):
            return GRPCServer_pb2.LoginResult(Succeed  = False, Error = 1, SessionId = None,
                                         Email = None, Password = None, FirstName = None,
                                         LastName = None)
        else:
            if(db_password != password):
                return GRPCServer_pb2.LoginResult(Succeed  = False, Error = 2, SessionId = None,
                                         Email = None, Password = None, FirstName = None,
                                         LastName = None)
            else:
                user_sid = uuid.uuid1()
                connect_user.update({user_sid:user_id})
                return GRPCServer_pb2.LoginResult(Succeed  = True, Error = 0, SessionId = user_sid,
                                         Email = email, Password = db_password, FirstName = info[2],
                                         LastName = info[3])
        #return super().Login(request, context)

    def Logout(self, request, context):
        user_sid = request.SessionId    
        del connect_user[user_sid]
        return GRPCServer_pb2.StringResponse(PayLoad = "logout successfully")
        #return super().Logout(request, context)

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
