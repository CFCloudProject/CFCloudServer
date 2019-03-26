import threading
import os
import S3Connector
from MysqlConnector import *
from Cache import *
from Models import User

# S3 Config
access_key = 'AKIAI3GZAZ77PXWO3HOQ'
secret_key = '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'
region = 'ap-southeast-1'
bucket = '19cloud1'

# EFS Config
efs_root = ''
efs_file_root = efs_root + '/namespaces'

# Mysql Config
mysql_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'BID_db',
    'charset': 'utf8'
    }

# sqlite3 config
sqlite3_db_path = efs_root + '/cfcloud.db'

class IdGenerator(object):

    def __init__(self, first):
        self.global_id = first
        self.lock = threading.Lock()

    def next(self):
        self.lock.acquire()
        self.global_id += 1
        id = self.global_id
        self.lock.release()
        return id

# Container Settings
container_max_size = 4 * 1024 * 1024
container_id_generator = IdGenerator(-1)
def get_new_container_id():
    return container_id_generator.next()

# Cache Settings
container_cache_max_capacity = 50
metadata_cache_max_capacity = 400

# User Id Generator
user_id_generator = IdGenerator(0)
def get_new_user_id():
    return user_id_generator.next()

def create_user_namesapce(user_id):
    namespace = efs_file_root + '/user_' + str(user_id)
    os.mkdir(namespace)

# Global Variables
global _server_user
global _S3Connector
global _BlockIndex
global _container_cache
global _metadata_cache
global _user_cache

def init():
    _server_user = User.User('server', None, 'CFCloud', 'Server')
    _S3Connector = S3Connector.S3Connector()
    _MysqlConnector = Connector.Connector()
    _BlockIndex = BlockIndex.BlockIndex(_MysqlConnector, 'BLOCK_INDEX')
    _container_cache = ContainerCache.ContainerCache(container_cache_max_capacity)
    _metadata_cache = MetadataCache.MetadataCache(metadata_cache_max_capacity)
    _user_cache = UserCache.UserCache(sqlite3_db_path)