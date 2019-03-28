import sys
import json
import os
import math
import operation_transform
import variables
import utils
from . import GRPCServer_pb2, GRPCServer_pb2_grpc


class GRPCServer_impl(GRPCServer_pb2_grpc.GRPCServerServicer):

    def Register(self, request, context):
        user = variables._user_session.register(request.Email, request.Password, request.FirstName, request.LastName)
        if user is None:
            return GRPCServer_pb2.RegisterResult(Succeed = False, Error = 1)
        else:
            utils.create_user_namespace(user['user_id'])
            return GRPCServer_pb2.RegisterResult(Succeed = True, Error = 0)

    def Login(self, request, context):
        login_result = variables._user_session.login(request.Email, request.Password)
        if login_result['code'] == 0:
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
        variables._user_session.logout(session_id)
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
        return GRPCServer_pb2.StringResponse(PayLoad = '')

    def UploadBlock(self, request_iterator, context):
        
        return GRPCServer_pb2.StringResponse(PayLoad = '')

    def Download(self, request, context):
        return super().Download(request, context)

    def DownloadBlock(self, request_iterator, context):
        return super().DownloadBlock(request_iterator, context)

    def GetMetadata(self, request, context):
        return super().GetMetadata(request, context)

    def ListFolder(self, request, context):
        return super().ListFolder(request, context)
