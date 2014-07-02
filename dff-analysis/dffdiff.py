import numpy as np
from dffreader import DffReader
import sys

class DffDiff:
    
    def __init__(self, dff1, dff2):
        
        reader1 = DffReader(dff1)
        reader2 = DffReader(dff2)
        
        self.defX1 = reader1.defX[10:-10,10:-10]
        self.defX2 = reader2.defX[10:-10,10:-10]
        self.defY1 = reader1.defY[10:-10,10:-10]
        self.defY2 = reader2.defY[10:-10,10:-10]
        
    def supremums(self):
        
        absoluteX = np.absolute(self.defX1 - self.defX2)
        absoluteY = np.absolute(self.defY1 - self.defY2)
        
        supremumX = np.amax(absoluteX)
        supremumY = np.amax(absoluteY)
        
        return (supremumX, supremumY)
    
    def standardDeviations(self):
        
        absoluteX = np.absolute(self.defX1 - self.defX2)
        absoluteY = np.absolute(self.defY1 - self.defY2)
        
        stdX = np.std(absoluteX)
        stdY = np.std(absoluteY)
        
        return (stdX, stdY)
    
if __name__=="__main__":
    
    diff = DffDiff(*sys.argv[1:])
    print "Supremums (x,y):"
    print diff.supremums()
    print "Standard deviations (x,y):"
    print diff.standardDeviations()
