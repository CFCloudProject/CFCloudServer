#-*- coding:UTF-8 -*-

import pickle
import os
#import VersionVector

class Metadata(object):
    """description of class"""
    def __init__(self, time = None, size = None):
        self.time = time
        self.shared_user = []
        self.size = size
        #self.vv = VersionVector()        
    def addUser(self, user):
        self.shared_user.append(user)
    def readMetadata(self, filepath):
        if(os.path.exists(filepath)):
            fp = open(filepath, 'rb')
            self = pickle.loads(fp.read())
            return self
        else:
            return False
    def writeMetadata(self, filepath):
        fp = open(filepath, 'wb')
        metadatastr = pickle.dumps(self)
        fp.write(metadatastr)
        fp.close()

data = Metadata('03/22',1024)
data.writeMetadata("test2.txt")
new = Metadata()
new = new.readMetadata("test2.txt")

    
