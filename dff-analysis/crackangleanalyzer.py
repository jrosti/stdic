from crackangle import CrackAngle
from glob import glob
from os import path
from itertools import izip
import matplotlib.pyplot as mpl
import numpy as np

class CrackAngleAnalyzer:
    
    def __init__(self, pointfile):
        pointfile = open(pointfile,'r')
        self.dfflist = []
        self.points = []
        for line in pointfile:
            linesplit = line.split()
            self.dfflist.append(linesplit[0])
            self.points.append([int(linesplit[1]), int(linesplit[2])])
        
    def getEs(self, angle):
        
        self.elist = []
        for dff, point in izip(self.dfflist, self.points):
            crackangle = CrackAngle(dff)
            self.elist.append(crackangle.getE(0, point[0], point[1], angle))         
            
    def plotEs(self):
        mpl.figure()
        mpl.hold(True)
        for e in self.elist:
            coefs, startindex, endindex = self._findR(e)
            if endindex - startindex < 20:
                continue
            rrange = np.arange(1,endindex-startindex+1)
            enew = e[startindex:endindex]
            mpl.plot(np.log(rrange), np.log(enew),'o', label="range %d to %d from cracktip" % (startindex,endindex))
            mpl.plot(np.log(rrange), coefs[0]*np.log(rrange) + coefs[1], label="coefs=%f,%f" % (coefs[0], coefs[1]))
            mpl.legend()
        mpl.show()
        
    def _findR(self, e):
        bestfit = 1000
        rrange = np.arange(0, e.shape[0])
        for index in xrange(1,e.shape[0]-1,5):
            for index2 in xrange(index + 1, e.shape[0]):
                raxis = np.log(rrange[1:index2-index + 1])
                rvalues = np.log(e[index:index2])
                try:
                    coefs = np.polyfit(raxis, rvalues, 1)
                except TypeError:
                    continue
                fit = abs(coefs[0] + 0.5)
                if fit < bestfit:
                    bestcoefs = coefs
                    bestfit = fit
                    startindex = index
                    endindex = index2
        return [bestcoefs,startindex,endindex]
    
if __name__=="__main__":
    import sys
    analyzer = CrackAngleAnalyzer(sys.argv[1])
    analyzer.getEs(float(sys.argv[2]))
    analyzer.plotEs()