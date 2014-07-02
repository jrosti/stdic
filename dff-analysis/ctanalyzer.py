from glob import glob
from os import path
from os import mkdir
from itertools import izip
from itertools import cycle
import matplotlib.pyplot as mpl
import numpy as np
from ctoptimizer import CTOptimizer
from crackangle import CrackAngle

class CTAnalyzer:
    
    def __init__(self, optimizer, savefolder=None):

        self.savefolder = savefolder
        if self.savefolder != None:
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
        
        self.optimizer = optimizer
            
    def plotEs(self):
        
        dfflist = self.optimizer.dfflist
        eslist = self.optimizer.eslist
        bestpointlist = self.optimizer.bestpointlist
        
        coloriter = cycle(self.colorlist)
                
        for dff, es, point in izip(dfflist, eslist, bestpointlist):
            
            mpl.figure()
            mpl.hold(True)
            for i in range(0,2):
                e = es[i]
                color = coloriter.next()
                rrange = np.arange(e.shape[0])
                mpl.plot(rrange, e,'^',
                         color=color,
                         label="plot %d"
                         % i)
            mpl.legend(loc=3)
            mpl.title("%s: x=%.2f y=%.2f" % (path.basename(dff), point[0], point[1]))
            if self.savefolder != None:
                dffnumber = int((path.basename(dff).split('.')[0]).split('-')[-1])
                mpl.savefig(path.join(self.savefolder,'%d-eyy.eps' % dffnumber))
            
    def plotEsLog(self):
        
        dfflist = self.optimizer.dfflist
        eslist = self.optimizer.eslist
        bestpointlist = self.optimizer.bestpointlist
        
        coloriter = cycle(self.colorlist)
                
        for dff, es, point in izip(dfflist, eslist, bestpointlist):
            
            mpl.figure()
            mpl.hold(True)
            for i in range(0,2):
                e = es[i]
                color = coloriter.next()
                rrange = np.arange(e.shape[0])
                mpl.plot(np.log10(rrange), np.log10(e),'^', 
                         color=color,
                         label="plot %d"
                         % i)
                mpl.plot(np.log10(rrange), -0.5*np.log10(rrange),'-', 
                         color=color,
                         label="-0.5 %d"
                         % i)
                
            mpl.legend(loc=3)
            mpl.title("%s: x=%.2f y=%.2f" % (path.basename(dff), point[0], point[1]))
            if self.savefolder != None:
                dffnumber = int((path.basename(dff).split('.')[0]).split('-')[-1])
                mpl.savefig(path.join(self.savefolder,'%d-log.eps' % dffnumber))
            
    def plotFits(self, save=False):
        
        dfflist = self.optimizer.dfflist
        eslist = self.optimizer.eslist
        bestpointlist = self.optimizer.bestpointlist
        coefslist = self.optimizer.coefslist
        indiceslist = self.optimizer.indiceslist
        
        coloriter = cycle(self.colorlist)
                
        for dff, es, coefs, indices, point in izip(dfflist,eslist, coefslist, indiceslist, bestpointlist):
            
            mpl.figure()
            mpl.hold(True)
            for i in range(0,2):
                e = es[i]
                coef = coefs[i]
                indice = indices[i]
                
                color = coloriter.next()
                e = e[indice:indice+50]
                rrange = np.arange(e.shape[0])
                mpl.plot(np.log10(rrange), np.log10(e),'^', color=color)
                mpl.plot(np.log10(rrange), coef[0]*np.log10(rrange)+coef[1], 
                         color=color,
                         label="plot %d: coefs=%.3f, %.3f from distance %d" 
                         % (i, coef[0],coef[1], indice))
                
            mpl.legend(loc=3)
            mpl.title("%s: x=%.2f y=%.2f" % (path.basename(dff), point[0], point[1]))
            if self.savefolder != None:
                dffnumber = int((path.basename(dff).split('.')[0]).split('-')[-1])
                mpl.savefig(path.join(self.savefolder,'%d-fit.eps' % dffnumber))           
            
    def plotEsAverage(self):
        
        dfflist = self.optimizer.dfflist
        eslist = self.optimizer.eslist
        bestpointlist = self.optimizer.bestpointlist
        
        samepoints = 1
        referencepoint = bestpointlist[0]
        for point in bestpointlist[1:]:
            if point == referencepoint:
                samepoints += 1
            else:
                break
        
        coloriter = cycle(self.colorlist)
                
        for i in xrange(0, len(dfflist), samepoints):
            mpl.figure()
            mpl.hold(True)
            dffnumber = int((path.basename(dfflist[i]).split('.')[0]).split('-')[-1])
            for j in range(0,2):
                e = 0
                
                for k in xrange(0,samepoints):
                    es = eslist[i+k]
                    e += es[j]
                    
                e = e/samepoints
                color = coloriter.next()
                rrange = np.arange(e.shape[0])
                mpl.plot(rrange, e,'^',
                         color=color,
                         label="plot %d"
                         % j)
            mpl.legend(loc=3)
            mpl.title("average eyy of pictures %d-%d: x=%.2f y=%.2f" % (dffnumber, dffnumber+samepoints, point[0], point[1]))
            if self.savefolder != None:
                mpl.savefig(path.join(self.savefolder,'%d-%d-average-eyy.eps' % (dffnumber,dffnumber+samepoints)))
            
        
    def plotEsLogAverage(self):
        
        dfflist = self.optimizer.dfflist
        eslist = self.optimizer.eslist
        bestpointlist = self.optimizer.bestpointlist
        
        samepoints = 1
        referencepoint = bestpointlist[0]
        for point in bestpointlist[1:]:
            if point == referencepoint:
                samepoints += 1
            else:
                break
        
        coloriter = cycle(self.colorlist)
                
        for i in xrange(0, len(dfflist), samepoints):
            mpl.figure()
            mpl.hold(True)
            dffnumber = int((path.basename(dfflist[i]).split('.')[0]).split('-')[-1])
            for j in range(0,2):
                e = 0
                
                for k in xrange(0,samepoints):
                    es = eslist[i+k]
                    e += es[j]
                    
                e = e/samepoints
                color = coloriter.next()
                rrange = np.arange(e.shape[0])
                mpl.plot(np.log10(rrange), np.log10(e),'^',
                         color=color,
                         label="plot %d"
                         % j)
                mpl.plot(np.log10(rrange), -0.5*np.log10(rrange),'-', 
                         color=color,
                         label="-0.5 %d"
                         % j)
            mpl.legend(loc=3)
            mpl.title("average eyy of pictures %d-%d: x=%.2f y=%.2f on log scale" % (dffnumber, dffnumber+samepoints, point[0], point[1]))
            if self.savefolder != None:
                mpl.savefig(path.join(self.savefolder,'%d-%d-average-log.eps' % (dffnumber,dffnumber+samepoints)))

            
    def plotFitAverage(self):
        
        eslist = self.optimizer.eslist
        
        earray = self._cutEs(eslist)
        e = np.average(earray, 0)
        
        coloriter = iter(self.colorlist)
        color = coloriter.next()
        rrange = np.arange(e.shape[0])
        mpl.plot(np.log10(rrange), np.log10(e),'^', 
                 color=color,
                 label="average over multiple dffs on log10")
        mpl.legend(loc=3)
        mpl.title("average over multiple dffs on log10")
        if self.savefolder != None:
            mpl.savefig(path.join(self.savefolder,'average-log.eps')) 
    
    def plotEsAll(self):
        
        eslist = self.optimizer.eslist
        
        earray = self._cutEs(eslist)
        e = np.average(earray, 0)
        
        coloriter = iter(self.colorlist)
        color = coloriter.next()
        rrange = np.arange(e.shape[0])
        mpl.plot(rrange, e,'^',
                 color=color,
                 label="average over multiple dffs")
        mpl.legend(loc=3)
        mpl.title("average over multiple dffs")
        if self.savefolder != None:
            mpl.savefig(path.join(self.savefolder,'average-eyys.eps'))
        
    def _cutEs(self, eslist):
        
        minsize = 10000
        for es in eslist:
            for e in es:
                if e.shape[0] < minsize:
                    minsize = e.shape[0]
        elist = []
        for es in eslist:
            for e in es:
                elist.append(e[:minsize])
        elist = np.asarray(elist,dtype=float)
        return elist
        
        
    def show(self):
        mpl.show()
    
if __name__=="__main__":
    import sys
    
    if len(sys.argv) < 3:
        raise Exception("Three arguments required.")
    
    command = int(sys.argv[1])
    optimizer = CTOptimizer(sys.argv[2])
    optimizer.optimize("none")
        
    try:
        folder = sys.argv[3]
        analyzer = CTAnalyzer(optimizer, folder)
        show = False
    except IndexError:    
        analyzer = CTAnalyzer(optimizer)
        show = True
        
    if (command == 0):
        analyzer.plotEs()
    elif (command == 1):
        analyzer.plotEsLog()
    elif (command == 2):
        analyzer.plotFits()
    elif (command == 3):
        analyzer.plotEsAverage()
    elif (command == 4):
        analyzer.plotEsLogAverage()
        
    if show:
        analyzer.show()
        
    