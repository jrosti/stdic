
from criterion import Criterion
import numpy as np
from scipy.ndimage.interpolation import map_coordinates
from scipy.integrate import simps

class YInt(Criterion):
        
    def __init__(self, data, shape, step):
        Criterion.__init__(self, data, shape, step)
    
    def evaluate(self, y, x):
        
        #Calculates the maximum length from point to the edges.
        
        maximum_length = np.min([y+1,self.shape[0]-y])
        
        # Creates an indexing array from point to the edge with spacing of 1 pixel.
        stepsize = 1.0/self.step
        indexarray = np.r_[0:maximum_length:stepsize]
        
        # Coordinate arrays for both the positive and the negative e.
        coords1 = np.asarray([float(y)/self.step-indexarray,float(x)/self.step + np.zeros_like(indexarray)])
        coords2 = np.asarray([float(y)/self.step+indexarray,float(x)/self.step + np.zeros_like(indexarray)])
    
        # Values of the array at these locations.
        e1 = map_coordinates(self.data, coords1, output=float, order=3)
        e2 = map_coordinates(self.data, coords2, output=float, order=3)
                                
        # Integral of e:s with each other.
        integral = simps(e1*e2)
        
        return -integral