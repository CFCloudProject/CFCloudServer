import pickle
import os
import json
import threading
import Global
from . import VersionVector, User

class Metadata(object):

    def __init__(self, tag, name, fullpath, size, rev, 
                 creation_time, modified_time, modifier, 
                 owner, is_shared, sharedusers, versions = None):
        self.attributes = {}
        self.attributes['tag'] = tag                           # 'File' or 'Folder'
        self.attributes['name'] = name
        self.attributes['fullpath'] = fullpath
        self.attributes['size'] = size
        self.attributes['rev'] = rev
        self.attributes['creation_time'] = creation_time
        self.attributes['modified_time'] = modified_time
        self.attributes['modifier'] = modifier
        self.attributes['owner'] = owner
        self.attributes['is_shared'] = is_shared
        self.attributes['sharedusers'] = sharedusers
        if versions is None:
            if tag == 'File':
                self.versions = VersionVector.VersionVector()
            else:
                self.versions = None
        else:
            self.versions = versions
        self.dirty = False
        if tag == 'File':
            self.meta_path = Global.efs_file_root + '/user_' 
            + str(owner.userid) + fullpath + '.metadata'
        else:
            self.meta_path = Global.efs_file_root + '/user_' 
            + str(owner.userid) + fullpath + '/.metadata'
        self.lock = threading.RLock()

    def set_attribute(name, attribute):
        self.lock.acquire()
        self.attributes[name] = attribute
        self.dirty = True
        self.lock.release()

    def share(self, user):
        self.lock.acquire()
        self.attributes['is_shared'] = True
        self.attributes['sharedusers'].append(user)
        self.dirty = True
        self.lock.release()

    def to_dict_attributes(self):
        self.lock.acquire()
        dict = {}
        dict['tag'] = self.attributes['tag']                          # string
        dict['name'] = self.attributes['name']                        # string
        dict['fullpath'] = self.attributes['fullpath']                # string
        dict['size'] = self.attributes['size']                        # int
        dict['rev'] = self.attributes['rev']                          # int
        dict['creation_time'] = self.attributes['creation_time']      # int
        dict['modified_time'] = self.attributes['modified_time']      # int
        dict['modifier'] = self.attributes['modifier'].__dict__       # User
        dict['owner'] = self.attributes['owner'].__dict__             # User
        dict['is_shared'] = self.attributes['is_shared']              # bool
        shared_users = []
        for user in self.attributes['sharedusers']:
            shared_users.append(user.__dict__)
        dict['sharedusers'] = shared_users                            # [User]
        self.lock.release()
        return dict

    def to_dict(self):
        self.lock.acquire()
        dict = self.to_dict_attributes()
        if self.versions is not None:
            dict['versions'] = self.versions.to_dict()
        self.lock.release()
        return dict

    def to_json_string(self):
        self.lock.acquire()
        dict = self.to_dict_attributes()
        self.lock.release()
        return json.dumps(dict)

    def write_back(self):
        self.lock.acquire()
        if self.dirty:
            fp = open(self.meta_path, 'wb')
            pickle.dump(self.to_dict(), fp)
            fp.close()
            self.dirty = False
        self.lock.release()

def from_dict(dict):
    tag = dict.get('tag')
    name = dict.get('name')
    fullpath = dict.get('fullpath')
    size = dict.get('size')
    rev = dict.get('rev')
    creation_time = dict.get('creation_time')
    modified_time = dict.get('modified_time')
    modifier = User.from_dict(from_dict.get('modifier'))
    owner = User.from_dict(from_dict.get('owner'))
    is_shared = dict.get('is_shared')
    shared_users = []
    for user in dict.get('sharedusers'):
        shared_users.append(User.from_dict(user))
    versions = VersionVector.from_dict(dict.get('versions'))
    return Metadata(tag, name, fullpath, size, rev, 
                    creation_time, modified_time, modifier, 
                    owner, is_shared, shared_users, versions)

def load(path):
    if(os.path.exists(path)):
        fp = open(path, 'rb')
        dict = pickle.load(fp)
        fp.close()
        return from_dict(dict)
    else:
        return None

    
