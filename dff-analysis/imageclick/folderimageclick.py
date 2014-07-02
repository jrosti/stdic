from glob import glob
from os import path
from imageclick import ImageClick
import sys

class FolderImageClick:
    
    def __init__(self, imageFolder, outputname, skip):
        
        self.imageFolder = imageFolder
        self.outputname = outputname        
        images = glob(path.join(imageFolder,'*.tiff'))
        images.sort()
        self.images = images[0:len(images):skip]
        
    def clickImages(self):
        self.pointlist = []
        for image in self.images:
            fclick = ImageClick(image)
            fclick.main()
            try:
                x = fclick.x
                y = fclick.y
                self.writePoint(image, x, y)
            except AttributeError:
                continue
        
    def writePoint(self, image, x, y):
        pointfile = open(self.outputname,'a')
        pointfile.write("%s %d %d\n" % (image, x, y))
        pointfile.close()
        
if __name__=="__main__":
    imageFolder, outputname, skip = sys.argv[1:4]
    controller = FolderImageClick(imageFolder, outputname, int(skip))
    controller.clickImages()