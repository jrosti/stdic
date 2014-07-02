from glob import glob
from os import path
import re
from itertools import izip

class FolderScan:
    
    def __init__(self, folder):
        self.filelist = glob(path.join(folder, '*'))
        
    def findWithExpression(self, regexpression):
        
        filelist = []
                
        filenamelist = map(path.basename, self.filelist)
        
        pattern = re.compile(regexpression)
        
        for itemname, item in izip(filenamelist,self.filelist):
            if pattern.match(itemname) != None:
                filelist.append(item)
                
        return filelist
