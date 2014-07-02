import numpy as np

class CriterionFactory:

    def __init__(self):
        
        from yint import YInt
        from logfit import LogFit
        
        self.criterions = dict({
                               "yint":YInt,
                               "logfit":LogFit
                               })
    
    def getCriterionClass(self, name):
        return self.criterions[name]

class Criterion:
    
    def __init__(self, data, shape, step):
        self.data = data
        self.shape = shape
        self.step = step

    def evaluateArray(self, skip, intervaly, intervalx):
        # Coordinate arrays.
        rangey = np.r_[0:self.shape[0]:skip]
        rangex = np.r_[0:self.shape[1]:skip]
        
        leny = rangey.shape[0]
        lenx = rangex.shape[0]
                
        # Array to house the values.
        values = np.zeros([leny,lenx], dtype=float)
        
        # Truth arrays that determine the area of interest.
        booleany = (rangey >= intervaly[0])*(rangey <= intervaly[1])
        booleanx = (rangex >= intervalx[0])*(rangex <= intervalx[1])
                
        for y in np.arange(leny):
            for x in np.arange(lenx):
                # If point belongs to the area of interest, integrate it.
                if booleany[y] and booleanx[x]:
                    values[y,x] = self.evaluate(rangey[y], rangex[x])
                    
        return values
    
    def getMinimum(self, skip, intervaly, intervalx):
        values = self.evaluateArray(skip, intervaly, intervalx)
        y,x = np.unravel_index(np.argmin(values), values.shape)
        y = skip*y
        x = skip*x
        
        return (y,x)
                    
    def evaluate(self, y, x):
        return 0