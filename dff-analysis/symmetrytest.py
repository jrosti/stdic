import numpy as np
from scipy.integrate import simps
import sys
from crackangle import CrackAngle
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d.axes3d import Axes3D
from os.path import basename
from scipy.signal import medfilt2d

class SymmetryTest:
    
    def __init__(self, pointfile, index):
        
        pointfile = open(pointfile, 'r')
        lines = pointfile.readlines()
        
        dff, x, y = lines[index-1].split()
        
        self.name = basename(dff)
        
        self.x = float(x)
        self.y = float(y)
        
        self.crackangle = CrackAngle(dff)
        
    def plotIntegral(self,skip=10):
        
        xsize = self.crackangle.derY.shape[1]*self.crackangle.step
        
        rangex = np.r_[0:xsize:skip]
        rangey = np.asarray([self.y])
                
        integrals, lengths = self._integrateEs(rangex, rangey)
            
        mpl.figure()
        mpl.plot(rangex, integrals, color='r')
        mpl.title("%s Skip: %d\nValues of Eyy-integrals" % (self.name, skip))
        mpl.figure()
        mpl.plot(rangex, lengths, color='b', label="Lengths of Eyys")
        
    def plotIntegral2D(self,skip=100):
        
        xsize = self.crackangle.derY.shape[1]*self.crackangle.step
        ysize = self.crackangle.derY.shape[0]*self.crackangle.step
        
        grid = np.mgrid[0:xsize:skip,0:ysize:skip]
        rangex = grid[0,:,0]
        rangey = grid[1,1,:]
    
        integrals, lengths = self._integrateEs(rangex, rangey)
        
        fig = mpl.figure()
        ax = Axes3D(fig)
        ax.plot_surface(grid[0],grid[1],integrals, rstride=1, cstride=1)
        mpl.title("%s Skip: %d\nValues of Eyy-integrals" % (self.name, skip))
        
    def _integrateEs(self, rangex, rangey):
        
        lenx = rangex.shape[0]
        leny = rangey.shape[0]
        
        integrals = np.empty([lenx,leny],dtype=float)
        lengths = np.empty([lenx,leny],dtype=int)
        
        for y in np.arange(leny):
            for x in np.arange(lenx):
                e1, e2 = self.crackangle.getEs(rangex[x],rangey[y])
                length = np.min([e1.shape[0],e2.shape[0]])
                try:
                    integrals[x,y] = simps(e1[:length]*e2[:length])
                except IndexError:
                    integrals[x,y] = 0
                lengths[x,y] = length
        return integrals, lengths
    
    def show(self):
        
        mpl.show()
        
if __name__=="__main__":
    command = int(sys.argv[3])
    tester = SymmetryTest(sys.argv[1], int(sys.argv[2]))
    if command == 0:
        try:
            tester.testIntegral(int(sys.argv[4]))
        except IndexError:
            tester.testIntegral()
    elif command == 1:
        try:
            tester.plotIntegral2D(int(sys.argv[4]))
        except IndexError:
            tester.plotIntegral2D()
        
    tester.show()