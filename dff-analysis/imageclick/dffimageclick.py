from glob import glob
from os import path
from imageclick import ImageClick
import sys
import re
from itertools import izip

class DffImageClick:
    
    def __init__(self, dffFolder, outputname, skip):
        
        self.dffFolder = dffFolder
        self.outputname = outputname        
        dffs = glob(path.join(dffFolder,'*.dff'))
        dffs.sort(reverse=True)
        
        images = []
        for dff in dffs:
            images.append(self.getImage(dff))
                    
        self.dffs   = dffs[0:len(dffs):skip]
        self.images = images[0:len(images):skip]
        
    def getImage(self, dff):
        dff = open(dff,'r')
        
        format = '^% image1 filename : (?P<filename>.+)$'
        for line in dff:
            formatmatch = re.match(format,line)
            if formatmatch != None:
                return formatmatch.group('filename')
        
    def clickImages(self):
        self.pointlist = []
        for dff, image in izip(self.dffs, self.images):
            fclick = ImageClick(image)
            fclick.main()
            try:
                x = fclick.x
                y = fclick.y
                self.writePoint(dff, x, y)
            except AttributeError:
                continue
        
    def writePoint(self, dff, x, y):
        pointfile = open(self.outputname,'a')
        pointfile.write("%s %d %d\n" % (dff, x, y))
        pointfile.close()
        
if __name__=="__main__":
    dffFolder, outputname, skip = sys.argv[1:4]
    controller = DffImageClick(dffFolder, outputname, int(skip))
    controller.clickImages()