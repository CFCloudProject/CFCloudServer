from GRPCServer import *
from concurrent import futures
import grpc
import time

_port = '6060'
_one_day_in_seconds = 24 * 60 * 60

def server_start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10))
    GRPCServer_pb2_grpc.add_GRPCServerServicer_to_server(GRPCServerImpl.GRPCServerImpl(), server)
    server.add_insecure_port('0.0.0.0:' + _port)
    server.start()
    try:
        while True:
            time.sleep(_one_day_in_seconds)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    server_start()
