class Container(object):
    """description of class"""
    cur_id = -1  # start from 0,1,2 ....这个id是所有container共享的
    def __init__(self):
        
        self.id = self.cur_id + 1
        self.units = [0]*1024*CONTAINSIZE
        self.conseEmptyUnits = [n for n in range(0,1024*CONTAINSIZE,1)]
        self.discEmptyUnits = []
        self.dirty = 0
        self.local = True
    def writeContainer(self, unitid, data, size):
        pos = 0
        global blockIndexId 
        blockIndexId += 1
        bid = blockIndexId
        self.dirty = 1
        while(1):
            self.units[unitid] = data[pos:pos+UNITSIZE]
            #print("write in container %d unit %d" %(contain.id,unitid))
            self.conseEmptyUnits.pop(0)
            unitid += 1
            size -= UNITSIZE
            pos += UNITSIZE
            if(length<=0): 
                break
        return bid
        


