import numpy as np
from scipy.signal import spline_filter
from dffreader import DffReader
from os import path
from glob import glob
from ctfinder import CTFinder

class CTFolder(CTFinder):
    
    def __init__(self, folder, criterionclass):
        
        # Reading folder.
        dffs = glob(path.join(folder,"*.dff"))
        dffs.sort()
        
        CTFinder.__init__(self, dffs, criterionclass)
         
    def getCrackTip(self, index):
        
        # Singe dff analysis.
        
        dff = self.dffs[index]
        
        print "Analyzing %s..." % path.basename(dff)
            
        dffreader = DffReader(dff)
        
        # Creation of y-directional strainrates.
        diffY = dffreader.defY - dffreader.origY
        derY = np.diff(diffY, 1, 0)
        
        # Exponential array [2^skiptimes, ..., 2]
        skiparray = np.vander([2],5)[0]
                
        # For loop that will iterate through different cratesizes.
        for i in np.arange(skiparray.shape[0]):
            
            skip = skiparray[i]
            # First iteration will go through the whole image.
            if i == 0:
                intervaly = [0,self.shape[0]]
                intervalx = [0,self.shape[1]]
            # Next iterations will integrate only the vicinity of last iterations best guess.
            else:
                oldskip = skiparray[i-1]
                intervaly = [y-oldskip,y+oldskip]
                intervalx = [x-oldskip,x+oldskip]
                
            print "Iteration %d with crate %d..." % ((i+1), skip)
            
            # Smoothing spline with length of cratesize. Used to minimize the chance of running into local maximums.
            data = spline_filter(derY, skip)
            
            criterion = self.criterionclass(data, self.shape, self.step)
            
            y,x = criterion.getMinimum(skip, intervaly, intervalx)            
            
            print "Criterion maximum at x=%d y=%d." % (x, y)
        
        return y,x
