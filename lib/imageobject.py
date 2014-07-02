from PIL import Image
from bz2 import BZ2File
import re
from os import path

class ImageObject:
    
    def __init__(self, filename, regexpression=None):
        
        self.filename = filename
        if regexpression != None:
            pattern = re.compile(regexpression)
            basename = path.basename(filename)
            matchdictionary = pattern.match(basename).groupdict()
            for key in matchdictionary:
                setattr(self,key, matchdictionary[key])
            
    def getImage(self):
        suffix = self.filename.split('.')[-1]
        if suffix == 'bz2':
            imagefile = BZ2File(self.filename, 'r')
        else:
            imagefile = self.filename
        return Image.open(imagefile,'r')
