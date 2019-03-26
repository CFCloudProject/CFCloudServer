import os
from Models.Container import Container
from Global import _container_cache

class PSINode(object):
    """description of class"""
    def __init__(self):
        self.paths = set()
        self.files = set()
        self.containers = []
        self.children = []
    def addPath(self, path):
        self.paths.add(path)
    def addFile(self, file):
        self.files.add(file)
    def addContainer(self, container):
        self.containers.append(container)
    def addChild(self, child):
        self.children.append(child)
        
    def checkPath(self, filepath):
        if(len(self.children)==0):
            return 0,0
        else:
            longest = 0
            node = None
            for kid_node in self.children:
                for path in kid_node.paths:
                    length = len(path)
                    if(filepath[0:length] == path and length>longest):
                        #print(unmatch_path[0:length], path, length)
                        longest = length
                        node = kid_node
            return longest, node
        
    def checkFileContainer(self, filepath, size):
        self.addFile(filepath)
        if(len(self.containers)==0):
            c = Container()
            _container_cache.addContainer(c)
            self.addcontainer(c)
            return c, c.id, 0
        else:
            for container in self.containers:
                if(len(container.conseEmptyUnits)*UNITSIZE > size):
                    return container, container.id, container.conseEmptyUnits[0]
            c = Container()
            _container_cache.addContainer(c)
            self.addcontainer(c)
            return c, c.id, 0
        
    def checkDirContainer(self, filepath, match_point, size):
        if(len(self.containers)==0):
            #print('here')
            c = Container()
            _container_cache.addContainer(c)
            self.addContainer(c)
            self.addFile(filepath)
            return c, c.id, 0
        else:
            for container in self.containers:
                if(len(container.conseEmptyUnits)*UNITSIZE > size):
                    self.addFile(filepath)
                    return container, container.id, container.conseEmptyUnits[0]
            new_node = PSINode()    
            cur_dir = filepath[:match_point]
            cur_dir = cur_dir + '/' + filepath[match_point:].split('/',2)[1]
            new_node.addPath(cur_dir)
            new_node.addFile(filepath)
            c = Container()
            _container_cache.addContainer(c)
            new_node.addContainer(c)
            self.addChild(new_node)
            return c, c.id, 0
    
    # 返回container, unit_id
    def recAddNode(self, filepath, match_point, size):
        match_len, node = self.checkPath(filepath)
        if(match_len==0):
            print('current match part '+filepath[0:match_point])
            print('current unmatch part '+filepath[match_point:])
            unmatch_path = filepath[match_point:]
            filename = '/'+os.path.split(filepath)[1]
            if(unmatch_path == filename):
                #print("you arrive in the file name")
                container, containid, unitid = self.checkFileContainer(filepath, size) 
                #print(contain, containid, unitid)
                return container, containid, unitid
            else:
                contain, containid, unitid = self.checkDirContainer(filepath, match_point, size)            
                return contain, containid, unitid
        else:
            match_point = match_len
            container, containid, unitid = self.recAddNode(filepath, match_point, size)
            return container, containid, unitid


