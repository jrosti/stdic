from glob import glob
from os import path
from os import mkdir
from itertools import izip
from itertools import cycle
import matplotlib.pyplot as mpl
import numpy as np
from dffreader import DffReader

class SpeedAnalyzer:
    
    def __init__(self, pointfilename, savefolder=None):
        
        pointfile = open(pointfilename,'r')
        self.dfflist = []
        pointlist = []
        for line in pointfile:
            linesplit = line.split()
            self.dfflist.append(linesplit[0])
            pointlist.append([float(linesplit[1]), float(linesplit[2])])
            
        self.points = np.asfarray(pointlist)[::-1,:]

        self.savefolder = savefolder
        if self.savefolder != None:
            self.savename = path.basename(pointfilename).split('.')[0]
            if not path.exists(self.savefolder):
                mkdir(self.savefolder)
                
        self.colorlist = [
                          'b',
                          'r',
                          'g',
                          'k',
                          'c',
                          'y',
                          'm'        
                          ]
        
        
    def plotPositions(self):
        
        dffreader = DffReader(self.dfflist[0])
        shape = dffreader.origY.shape
        step = dffreader.step
                
        mpl.figure()   
        mpl.hold(True)
        
        x = self.points[:,0]
        y = self.points[:,1]

        mpl.plot(x,y,'.')
        mpl.axis([0,step*shape[1],0,step*shape[0]])
        mpl.gca().invert_yaxis()
        mpl.title("Positions of cracktip on the image.")
        
        if self.savefolder != None:
            mpl.savefig(path.join(self.savefolder, "%s-posimg.png" % self.savename))
            
        pointsrange = np.arange(x.shape[0])
        mpl.figure()
        mpl.hold(True)
        xpoly = np.polyfit(pointsrange,x,deg=1)
        ypoly = np.polyfit(pointsrange,y,deg=1)
        mpl.plot(pointsrange, x, '.', color='r', label="X-coordinate")
        mpl.plot(pointsrange, xpoly[0]*pointsrange + xpoly[1], '-', color='k', label="Polyfit p1=%f, p2=%f" % (xpoly[0], xpoly[1]))
        mpl.plot(pointsrange, y, '.', color='b', label="Y-coordinate")
        mpl.plot(pointsrange, ypoly[0]*pointsrange + ypoly[1], '-', color='k', label="Polyfit p1=%f, p2=%f" % (ypoly[0], ypoly[1]))
        mpl.legend()
        
    def plotSpeeds(self):
        
        diffs = np.diff(self.points,1,0)
        vx = -1*diffs[:,0]
        vy = -1*diffs[:,1]
        datapoints = self.points.shape[0]
        
        mpl.figure()
        mpl.hold(True)
        
        mpl.plot(vx, 'r', label="X-directional velocity")
        mpl.plot(vy, 'b', label="Y-directional velocity")
        
        v = np.sqrt(np.power(vx,2)+ np.power(vy,2))
        mpl.plot(v,'g', label="Norm of velocity")
        
        mpl.title("Velocities of cracktip")
        mpl.legend()
        
        if self.savefolder != None:
            mpl.savefig(path.join(self.savefolder, "%s-velos.png" % self.savename))
        
        mpl.figure()
        mpl.hold(True)
        
        vxave = (vx[0:-2] + vx[1:-1] + vx[2:])/3
        vyave = (vy[0:-2] + vy[1:-1] + vy[2:])/3
        
        mpl.plot(vxave, 'r', label="X-directional velocity")
        mpl.plot(vyave, 'b', label="Y-directional velocity")
         
        vave = np.sqrt(np.power(vxave,2)+ np.power(vyave,2))  
        mpl.plot(vave,'g', label="Norm of velocity")
        
        mpl.title("Velocities of cracktip with running average of 3")
        mpl.legend()
        
        if self.savefolder != None:
            mpl.savefig(path.join(self.savefolder, "%s-velos-ave.png" % self.savename))
        
    def show(self):
        mpl.show()
    
if __name__=="__main__":
    import sys
    
    pointfile = sys.argv[1]
        
    try:
        folder = sys.argv[2]
        analyzer = SpeedAnalyzer(pointfile, folder)
        show = False
    except IndexError:    
        analyzer = SpeedAnalyzer(pointfile)
        show = True
        
    analyzer.plotPositions()
    analyzer.plotSpeeds()
        
    if show:
        analyzer.show()
    
