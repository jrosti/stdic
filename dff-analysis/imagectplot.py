import sys
import numpy as np
import matplotlib.pyplot as mpl
import matplotlib.image as img
from dffreader import DffReader
from crackangle import CrackAngle

class ImageCTPlot:

    def __init__(self, imagename, x, y):
        
        self.image = img.imread(imagename)
        self.x = x
        self.y = y
                
    def plotCT(self):
        
        fig = mpl.figure()
        ax = fig.add_subplot(111)
        
        mpl.imshow(self.image)
        mpl.axis("tight")
        
        ax.plot(self.x, self.image.shape[0] - self.y, 'o', color='r')
        mpl.gca().invert_yaxis()
        
        mpl.show()

if __name__ == "__main__":
    pointfile = open(sys.argv[1],'r')
    for line in pointfile:
        imagename, x, y = line.split()
        tipPlots = ImageCTPlot(imagename, float(x), float(y))
        tipPlots.plotCT()
        
#------------------------------------------------------------------------------