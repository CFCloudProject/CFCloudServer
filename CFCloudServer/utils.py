import config
import threading
import os
import six
import hashlib

class id_generator(object):

    def __init__(self, first):
        self.global_id = first
        self.lock = threading.Lock()

    def next(self):
        self.lock.acquire()
        self.global_id += 1
        id = self.global_id
        self.lock.release()
        return id

# container id generator
container_id_generator = id_generator(-1)
def get_new_container_id():
    return container_id_generator.next()

# user id generator
user_id_generator = id_generator(0)
def get_new_user_id():
   return user_id_generator.next()

# util methods
def create_user_namesapce(user_id):
    namespace = config.efs_file_root + '/user_' + str(user_id)
    if not os.path.exists(namespace):
        os.mkdir(namespace)

def get_true_path(user, path):
    user_root = config.efs_file_root + '/user_' + str(user.user_id)
    pos = path.find('/', 1)
    if pos != -1:
        linkpath = user_root + path[:path.find('/', 1)] + '.li'
    else:
        linkpath = user_root + path + '.li'
    if os.path.exists(linkpath):
        fp = open(path, 'r')
        per = fp.readline()
        fp.close()
        if pos != -1:
            ret = per + path[path.find('/', 1):]
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

def adler32(b):
    s1 = 1
    s2 = 0
    pos = 0
    remain = len(b)
    while remain > 0:
        n = remain if 3800 > remain else 3800
        remain -= n
        while n > 0:
            s1 += (b[pos] & 0xFF)
            s2 += s1
            pos += 1
            n -= 1
        s1 %= 65521
        s2 %= 65521
    ret = int2bytes(s2) + int2bytes(s1)
    return ret.hex()

def md5(b):
    m = hashlib.md5()
    m.update(b)
    return m.hexdigest()
