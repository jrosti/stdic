
from criterion import Criterion
import numpy as np
from scipy.ndimage.interpolation import map_coordinates
from scipy.integrate import simps

class LogFit(Criterion):
        
    def __init__(self, data, shape, step):
        Criterion.__init__(self, data, shape, step)
        
    def evaluate(self, y, x):
        
        #Calculates the maximum length from point to the edges.
        
        maximum_length = np.min([self.shape[1]-x,np.min([y+1,self.shape[0]-y])])
        
        # Creates an indexing array from point to the edge with spacing of 1 pixel.
        stepsize = 1.0/(np.sqrt(2)*self.step)
        indexarray = np.r_[0:maximum_length:stepsize]
        
        # Coordinate arrays for both the positive and the negative e.
        coords1 = np.asarray([float(y)/self.step-indexarray,float(x)/self.step + indexarray])
        coords2 = np.asarray([float(y)/self.step+indexarray,float(x)/self.step + indexarray])
    
        # Values of the array at these locations.
        e1 = map_coordinates(self.data, coords1, output=float, order=3)
        e2 = map_coordinates(self.data, coords2, output=float, order=3)
        
        # Logarithmic strain
        e1log = np.log(e1)
        e2log = np.log(e2)
        
        index = np.log(r_[0:e1.shape[0]])
        k11, k12 = np.polyfit(index, e1log, 1)
        k21, k22 = np.polyfit(index, e2log, 1)
        
        norm = 
                
        return -norm