import pickle
import os
import json
import threading
from . import VersionVector, User

class Metadata(object):

    def __init__(self, tag, name, fullpath, size, rev, creation_time, modified_time, modifier, owner, is_shared, sharedusers, versions = None):
        self.tag = tag
        self.name = name
        self.fullpath = fullpath
        self.size = size
        self.rev = rev
        self.creation_time = creation_time
        self.modified_time = modified_time
        self.modifier = modifier
        self.owner = owner
        self.is_shared = is_shared
        self.sharedusers = sharedusers
        if versions is None:
            if self.tag == 'File':
                self.versions = VersionVector.VersionVector()
            else:
                self.versions = None
        else:
            self.versions = versions
        self.lock = threading.RLock()

    def share(self, user):
        self.lock.acquire()
        self.is_shared = True
        self.sharedusers.append(user)
        self.lock.release()

    def to_dict_except_versions(self):
        self.lock.acquire()
        dict = {}
        dict['tag'] = self.tag                          # string
        dict['name'] = self.name                        # string
        dict['fullpath'] = self.fullpath                # string
        dict['size'] = self.size                        # int
        dict['rev'] = self.rev                          # int
        dict['creation_time'] = self.creation_time      # int
        dict['modified_time'] = self.modified_time      # int
        dict['modifier'] = self.modifier.__dict__       # User
        dict['owner'] = self.owner.__dict__             # User
        dict['is_shared'] = self.is_shared              # bool
        shared_users = []
        for user in self.sharedusers:
            shared_users.append(user.__dict__)
        dict['sharedusers'] = shared_users              # [User]
        # no need to send VersionVector to user
        self.lock.release()
        return dict

    def to_dict(self):
        self.lock.acquire()
        dict = self.to_dict_except_versions()
        if self.versions is not None:
            dict['versions'] = self.versions.to_dict()
        self.lock.release()
        return dict

    def to_json_string(self):
        self.lock.acquire()
        dict = self.to_dict_except_versions()
        self.lock.release()
        return json.dumps(dict)

    def to_metadata_file(self, file):
        self.lock.acquire()
        fp = open(filepath, 'wb')
        pickle.dump(self.to_dict(), fp)
        fp.close()
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

def from_metadata_file(file):
    if(os.path.exists(file)):
        fp = open(file, 'rb')
        dict = pickle.load(fp)
        return from_dict(dict)
    else:
        return None

    
