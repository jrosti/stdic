import numpy as np
from scipy.integrate import simps
from itertools import izip
from crackangle import CrackAngle

class CTOptimizer:
    
    def __init__(self, pointfile, output=None):
        
        self.optimizerdict = {
                              "none":self._NoneOptimizer,
                              "fit":self._FitOptimizer,
                              "symmetry":self._SymmetryOptimizer
                              }
        
        pointfile = open(pointfile,'r')
        self.dfflist = []
        self.pointlist = []
        for line in pointfile:
            linesplit = line.split()
            self.dfflist.append(linesplit[0])
            self.pointlist.append([float(linesplit[1]), float(linesplit[2])])
        
        self.bestpointlist = []
        
        self.eslist = []
        self.coefslist = []
        self.indiceslist = []
        
        self.output=output
        self.shape = None
        self.step = None
        
    def optimize(self, optimizer="symmetry"):
        
        optimizer = self.optimizerdict[optimizer]
        
        for dff, point in izip(self.dfflist, self.pointlist):
            crackangle = CrackAngle(dff)
            if (self.shape == None):
                self.step = crackangle.step
                self.shape = np.array([self.step * crackangle.shape[0], self.step * crackangle.shape[1]])
            bestpoint, es, coefs, indices = optimizer(crackangle, point)
            self.bestpointlist.append(bestpoint)
            self.eslist.append(es)
            self.coefslist.append(coefs)
            self.indiceslist.append(indices)
            if (self.output != None):
                self._exportPoints(dff, bestpoint)
                    
    def _NoneOptimizer(self, crackangle, point):
        
        e1 = crackangle.getE(point[0],point[1],45)
        e2 = crackangle.getE(point[0],point[1],-45)
        coefs1, indice1, fit1 = self._fitCoef(e1)
        coefs2, indice2, fit2 = self._fitCoef(e2)
                    
        return point, [e1,e2], [coefs1, coefs2], [indice1, indice2]
    
    def _SymmetryOptimizerNew(self,crackangle, point):
        
        interval = 10
        skip = 1
        secondinterval = 1
        secondskip = 0.25
        
        length_minimum = self._getMinLength(crackangle, point[0], point[1], interval)
        bestfit = 0
        
        x=point[0]
        for y in np.arange(point[1]-interval,point[1]+interval+1,skip):
            if self._isPointWithin(crackangle,x,y):
                e1 = crackangle.getE(x,y,45)
                e2 = crackangle.getE(x,y,-45)
                fit = simps(e1[:length_minimum]*e2[:length_minimum])
                if (fit > bestfit):
                    bestfit = fit
                    besty = y
                    
        if bestfit == 0:
            bestpoint = point
            e1 = crackangle.getE(bestpoint[0],bestpoint[1],45)
            e2 = crackangle.getE(bestpoint[1],bestpoint[1],-45)
            bestes = [e1,e2]
            print "integral negative for point %d,%d!" %(bestpoint[0], bestpoint[1])
        else:
            bestpoint = [bestx, besty]
            e1 = crackangle.getE(bestx,besty,45)
            e2 = crackangle.getE(bestx,besty,-45)
            bestes = [e1,e2]
            
            pass
            """
            length_minimum = self._getMinLength(crackangle, bestpoint[0], bestpoint[1], interval)
            for x in np.arange(bestpoint[0]-secondinterval,bestpoint[0]+secondinterval+1,secondskip):
                for y in np.arange(bestpoint[1]-secondinterval,bestpoint[1]+secondinterval+1,secondskip):
                    e1 = crackangle.getE(x,y,45)
                    e2 = crackangle.getE(x,y,-45)
                    fit = simps(e1[:length_minimum]*e2[:length_minimum])
                    if (fit > bestfit):
                        bestfit = fit
                        bestpoint = [x,y]
                        bestes = [e1,e2]
                        """
            

        print "point %d,%d ; bestpoint %f,%f ; fit=%f" % (point[0], point[1],bestpoint[0], bestpoint[1], bestfit)
                    
        coefs1, indice1, fit1 = self._fitCoef(bestes[0])
        coefs2, indice2, fit2 = self._fitCoef(bestes[1])
        
        return bestpoint, bestes, [coefs1, coefs2], [indice1, indice2]
    
    def _SymmetryOptimizer(self,crackangle, point):
        
        interval = 10
        skip = 1
        secondinterval = 1
        secondskip = 0.25
        
        bestfit = 0
        
        for x in np.arange(point[0]-interval,point[0]+interval+1,skip):
            for y in np.arange(point[1]-interval,point[1]+interval+1,skip):
                if self._isPointWithin(crackangle,x,y):
                    e1 = crackangle.getE(x,y,45)
                    e2 = crackangle.getE(x,y,-45)
                    elength = np.min([e1.shape[0],e2.shape[0]])
                    fit = simps(e1[:elength]*e2[:elength])
                    if (fit > bestfit):
                        bestfit = fit
                        bestpoint = [x,y]
                        bestes = [e1,e2]
                    
        if bestfit == 0:
            bestpoint = point
            e1 = crackangle.getE(bestpoint[0],bestpoint[1],45)
            e2 = crackangle.getE(bestpoint[1],bestpoint[1],-45)
            bestes = [e1,e2]
            print "integral negative for point %d,%d!" %(bestpoint[0], bestpoint[1])
        else:
            for x in np.arange(bestpoint[0]-secondinterval,bestpoint[0]+secondinterval+1,secondskip):
                for y in np.arange(bestpoint[1]-secondinterval,bestpoint[1]+secondinterval+1,secondskip):
                    e1 = crackangle.getE(x,y,45)
                    e2 = crackangle.getE(x,y,-45)
                    elength = np.min([e1.shape[0],e2.shape[0]])
                    fit = simps(e1[:elength]*e2[:elength])
                    if (fit > bestfit):
                        bestfit = fit
                        bestpoint = [x,y]
                        bestes = [e1,e2]
            

        print "point %d,%d ; bestpoint %f,%f ; fit=%f" % (point[0], point[1],bestpoint[0], bestpoint[1], bestfit)
                    
        coefs1, indice1, fit1 = self._fitCoef(bestes[0])
        coefs2, indice2, fit2 = self._fitCoef(bestes[1])
        
        return bestpoint, bestes, [coefs1, coefs2], [indice1, indice2]
            
    def _FitOptimizer(self, crackangle, point):
        
        interval = 5
        
        bestfit1 = 1000
        bestfit2 = 1000
        bestfits = 1000
        
        for x in np.arange(point[0]-interval,point[0]+interval+1):
            for y in np.arange(point[1]-interval,point[1]+interval+1):
                e1 = crackangle.getE(x,y,45)
                e2 = crackangle.getE(x,y,-45)
                coefs1, indice1, fit1 = self._fitCoefCond(e1)
                coefs2, indice2, fit2 = self._fitCoefCond(e2)
                fits = fit1 + fit2
                if ((fits < bestfits) and ((fit1<bestfit1 or fit2<bestfit2))):
                    bestfit1 = fit1
                    bestfit2 = fit2
                    bestfits = fits
                    bestes = [e1,e2]
                    bestcoefs = [coefs1, coefs2]
                    bestindices = [indice1, indice2]
                    bestpoint = [x,y]
                    
        print "point %d,%d ; bestpoint %d,%d ; fit=%f" % (point[0], point[1],bestpoint[0], bestpoint[1], bestfits)
                    
        return bestpoint, bestes, bestcoefs, bestindices
    
    def _fitCoef(self, e, start=10,end=61, skip=1):
        bestfit = 1000
        bestcoefs = np.array([0,0])
        bestindex = 0
        rrange = np.arange(e.shape[0])

        for index in rrange[start:end:skip]:
            esplice = e[index:index + end - start]
            rsplice = rrange[start:end]
            rvalues = np.log10(esplice[esplice > 0])
            raxis = np.log10(rsplice[esplice > 0])
            try:
                values = np.polyfit(raxis, rvalues, 1, full=True)
                coefs = values[0]
                rcond = values[3]
            except TypeError:
                continue
            fit = np.abs(coefs[0]+0.5)
            if fit < bestfit:
                bestcoefs = coefs
                bestfit = fit
                bestindex = index
        return bestcoefs, bestindex, bestfit
    
    def _fitCoefCond(self, e, start=10,end=61, skip=1):
        bestfit = 1000
        bestcoefs = np.array([0,0])
        bestindex = 0
        rrange = np.arange(e.shape[0])

        for index in rrange[start:end:skip]:
            esplice = e[index:index + end - start]
            rsplice = rrange[start:end]
            rvalues = np.log10(esplice[esplice > 0])
            raxis = np.log10(rsplice[esplice > 0])
            try:
                values = np.polyfit(raxis, rvalues, 1, full=True)
                coefs = values[0]
                rcond = values[3]
            except TypeError:
                continue
            fit = rcond[0]
            if fit < bestfit:
                bestcoefs = coefs
                bestfit = fit
                bestindex = index
        return bestcoefs, bestindex, bestfit
    
    def _getMinLength(self, crackangle, x, y, interval):
        k = np.sqrt(2)
        xdistance1 = k*(self.step*self.shape[1]-x+interval)
        xdistance2 = k*(x-interval)
        xmin = min(xdistance1,xdistance2)
        ydistance1 = k*(self.step*self.shape[0]-y+interval)
        ydistance2 = k*(y-interval)
        ymin = min(ydistance1,ydistance2)
        return int(np.floor(min(xmin,ymin)))
    
    def _isPointWithin(self, crackangle, x, y):
        if ((x<0) or (x>=self.shape[1])):
            return False
        elif ((y<0) or (y>=self.shape[0])):
            return False
        else:
            return True
    
    def _exportPoints(self, dff, bestpoint):
                
        output = open(self.output,'a')
        
        output.write("%s %f %f\n" % (dff, bestpoint[0], bestpoint[1]))
        
        output.close()
        
if __name__=="__main__":
    import sys
    if len(sys.argv) < 4:
        raise Exception("Three arguments required.")
    command = int(sys.argv[1])
    optimizer = CTOptimizer(sys.argv[2], sys.argv[3])
    if (command == 0):
        optimizer.optimize("none")
    elif (command == 1):
        optimizer.optimize("symmetry")
    elif (command == 2):
        optimizer.optimize("fit")