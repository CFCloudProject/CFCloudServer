import GRPCServer_pb2
import GRPCServer_pb2_grpc

class GRPCServerImpl(GRPCServer_pb2_grpc.GRPCServerServicer):

    def Register(self, request, context):
        return super().Register(request, context)

    def Login(self, request, context):
        return super().Login(request, context)

    def Logout(self, request, context):
        return super().Logout(request, context)

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
        return super().Upload(request, context)

    def UploadBlock(self, request_iterator, context):
        return super().UploadBlock(request_iterator, context)

    def Download(self, request, context):
        return super().Download(request, context)

    def DownloadBlock(self, request_iterator, context):
        return super().DownloadBlock(request_iterator, context)

    def GetMetadata(self, request, context):
        return super().GetMetadata(request, context)

    def ListFolder(self, request, context):
        return super().ListFolder(request, context)

    def GetToken(self, request, context):
        return super().GetToken(request, context)

    def ReturnToken(self, request, context):
        return super().ReturnToken(request, context)

    def CanModifyFolder(self, request, context):
        return super().CanModifyFolder(request, context)

