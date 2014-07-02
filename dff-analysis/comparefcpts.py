import numpy as np
import matplotlib.pyplot as mpl
from itertools import *
import sys

class CompareOptimizer:
    
    def __init__(self, pointfile1, pointfile2):
        
        self.colors = ['r','b']
        
        pointfiles = [open(pointfile1, 'r'), open(pointfile2, 'r')]
        
        filelength = None
        
        for fileindex in np.arange(len(pointfiles)):
            pointfile = pointfiles[fileindex]
            lines = pointfile.readlines()
            if filelength == None:
                filelength = len(lines)
                self.points = np.zeros([2,filelength,2],dtype=float)
            elif filelength != len(lines):
                raise Exception("Pointfiles must be of equal length.")
            for lineindex in np.arange(filelength):
                dff, x, y = lines[lineindex].split()
                self.points[fileindex,lineindex,:] = [y,x]
                
    def plotPositions(self):
        
        for k in np.arange(2):
            
            mpl.figure()
            mpl.hold(True)
            
            coloriter = cycle(self.colors)
            
            maxj = self.points.shape[1]
            for i in np.arange(2):
                mpl.plot(np.arange(maxj),
                         self.points[i,:,k],
                         color=coloriter.next(),
                         label="Coordinates of cracktips in %d direction" % k)
                mpl.legend()
                
    def plotDiffs(self):
        
        mpl.figure()
        mpl.hold(True)
        coloriter = cycle(self.colors)
        
        for k in np.arange(2):            
            maxj = self.points.shape[1]
            mpl.plot(np.arange(maxj),
                     (self.points[0,:,k] - self.points[1,:,k]),
                     color=coloriter.next(),
                     label="Difference of cracktip coordinates in %d direction" % k)
            mpl.legend()
            
    def show(self):
        mpl.show()
                
if __name__=="__main__":
    comparer = CompareOptimizer(*sys.argv[1:])
    comparer.plotPositions()
    comparer.plotDiffs()
    comparer.show()