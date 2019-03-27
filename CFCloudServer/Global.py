import threading
import os
import six
import hashlib

print("aaaa")
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



# util methods
def get_true_path(user, path):
    user_root = Global.efs_file_root + '/user_' + str(user.userid)
    pos = path.find('/', 1)
    if pos != -1:
        linkpath = user_root + path[0 : path.find('/', 1)] + '.li'
    else:
        linkpath = user_root + path + '.li'
    if os.path.exists(linkpath):
        fp = open(path, 'rb')
        per = fp.readline()
        fp.close()
        if pos != -1:
            ret = per + path[path.find('/', 1) : len(path)]
        else:
            ret = per
    else:
        ret = user_root + path
    return ret

def int2bytes(n):
    ret = b''
    while n > 0:
        m = n % 256
        ret = six.int2byte(m) + ret
        n = int(n / 256)
    return ret

def get_adler32(b):
    s1 = 1
    s2 = 0
    pos = 0
    remain = len(b)
    while remain > 0:
        n = remain if 3800 > remain else 3800
        remain -= n
        while n > 0:
            s1 = s1 + (b[pos] & 0xFF)
            s2 = s2 + s1
            pos += 1
            n -= 1
        s1 %= 65521
        s2 %= 65521
    ret = int2bytes(s2) + int2bytes(s1)
    return ret.hex()

def get_md5(b):
    m = hashlib.md5()
    m.update(b)
    return m.hexdigest()