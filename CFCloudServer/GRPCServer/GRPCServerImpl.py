import sys
from Models.VitrualBlock import VitrualBlock
from OT import OTFunctions
import json
import os
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
        user = Global._user_cache.get_user(request.SessionId)
        baserev = int(request.BaseRev)
        size = request.Size
        modified_time = request.ModifiedTime
        path = request.Path
        path = Global.get_true_path(user, path)
        rev, hashlist = Global._metadata_cache.create_temp_version(path + '.metadata', request.Path, user, modified_time, size, baserev)
        jstr = json.dumps({'rev': rev, 'blocks': hashlist})
        return GRPCServer_pb2.StringResponse(PayLoad = jstr)

    def UploadBlock(self, request_iterator, context):
        for request in request_iterator:
            user = Global._user_cache.get_user(request.SessionId)
            path = request.Path
            path = Global.get_true_path(user, path)
            base_rev = int(request.BaseRev)
            rev = int(request.Rev)
            base_index = request.BaseIndex
            index = request.Index
            confident = request.Confident
            hash = request.Hash
            data = request.Content
            if data is None:
                vblock = VitrualBlock(str(base_rev) + ':' + base_index, None, None, hash)
            else:
                if base_rev is None:
                    vblock = VitrualBlock(None, None, hash, hash)
                    writedata = True
                else:
                    if confident:
                        oldata = Global._metadata_cache.read_block(path + '.metadata', base_rev, int(base_index))
                        op_data = OTFunctions.oplist2bytes(OTFunctions.GenerateOpList(oldata, data))
                        if len(op_data) < len(data):
                            op_hash = Global.get_adler32(op_data) + Global.get_md5(op_hash)
                            vblock = VitrualBlock(str(base_rev) + ':' + base_index, op_hash, None, hash)
                            writedata = False
                        else:
                            vblock = VitrualBlock(None, None, hash, hash)
                            writedata = True
                    else:
                        baseindexs = base_index.split('|')
                        size = len(data)
                        op_data = None
                        for _data in Global._metadata_cache.read_blocks(path + '.metadata', base_rev, baseindexs):
                            _op_data = OTFunctions.oplist2bytes(OTFunctions.GenerateOpList(_data, data))
                            if (len(_op_data) < size):
                                size = len(_op_data)
                                op_data = _op_data
                        if op_data is None:
                            vblock = VitrualBlock(None, None, hash, hash)
                            writedata = True
                        else:
                            op_hash = Global.get_adler32(op_data) + Global.get_md5(op_hash)
                            vblock = VitrualBlock(str(base_rev) + ':' + base_index, op_hash, None, hash)
                            writedata = False
                if writedata:
                    # write data
                    pass
                else:
                    # write op
                    pass
            Global._metadata_cache.add_vitrual_block(path + '.metadata', rev, vblock)
        Global._metadata_cache.set_readable(path + '.metadata', rev)
        return GRPCServer_pb2.StringResponse(PayLoad = '')

    def Download(self, request, context):
        return super().Download(request, context)

    def DownloadBlock(self, request_iterator, context):
        return super().DownloadBlock(request_iterator, context)

    def GetMetadata(self, request, context):
        return super().GetMetadata(request, context)

    def ListFolder(self, request, context):
        return super().ListFolder(request, context)
