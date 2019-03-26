import S3Connector
from MysqlConnector import *
from Cache import *
from Models import User

#S3 Config
access_key = 'AKIAI3GZAZ77PXWO3HOQ'
secret_key = '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'
region = 'ap-southeast-1'
bucket = '19cloud1'

#Mysql Config
mysql_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'BID_db',
    'charset': 'utf8'
    }

#Container Settings
global_container_id = -1
container_max_size = 4 * 1024 * 1024
def get_new_container_id():
    global_container_id += 1
    return global_container_id

#Container Cache Settings
container_cache_max_capacity = 50

#Global Variables
_server_user = User.User('server', None, 'CFCloud', 'Server')
#_S3Connector = S3Connector.S3Connector()
#_MysqlConnector = Connector.Connector()
#_BlockIndex = BlockIndex.BlockIndex(_MysqlConnector, 'BLOCK_INDEX')
#_container_cache = ContainerCache.ContainerCache(container_cache_max_capacity)