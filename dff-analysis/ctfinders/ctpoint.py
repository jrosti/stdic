import numpy as np
from dffreader import DffReader
from scipy.signal import spline_filter
from os import path

from ctfinder import CTFinder

class CTPoint(CTFinder):
    
    def __init__(self, pointfile, criterionclass):
        
        pointfile = open(pointfile, 'r')
        
        dffs = []
        self.points = []
        # Reading pointfile.
        for line in pointfile:
            dff, x, y = line.split()
            dffs.append(dff)
            self.points.append([int(y), int(x)])

        CTFinder.__init__(self, dffs, criterionclass)
    
    def getCrackTip(self, index):
        
        dff = self.dffs[index]
        point = self.points[index]
        
        # Singe dff analysis.
        
        print "Analyzing %s..." % path.basename(dff)
            
        dffreader = DffReader(dff)
        
        # Creation of y-directional strainrates.
        diffY = dffreader.defY - dffreader.origY
        derY = np.diff(diffY, 1, 0)
        
        # Exponential array [2^skiptimes, ..., 2]
        skiparray = np.vander([2],4)[0]
                
        y = point[0]
        x = point[1]
        
        # For loop that will iterate through different cratesizes.
        for i in np.arange(skiparray.shape[0]):
            
            skip = skiparray[i]
            # Iterations will integrate only the vicinity of last iteration's best guess.
            # If it's the first iteration, the initial guess is taken from pointfile.
            if i==0:
                oldskip = 64
            else:
                oldskip = 2*skiparray[i-1]
                
            intervaly = [y-oldskip,y+oldskip]
            intervalx = [x-oldskip,x+oldskip]
                
            print "Iteration %d with crate %d..." % ((i+1), skip)
            
            # Smoothing spline with length of cratesize. Used to minimize the chance of running into local maximums.
            data = spline_filter(derY, skip)
            
            criterion = self.criterionclass(data, self.shape, self.step)
            
            y,x = criterion.getMinimum(skip, intervaly, intervalx)         
            
            print x,y   
            
            print "Criterion maximum at x=%d y=%d." % (x, y)
        
        return y,x
    