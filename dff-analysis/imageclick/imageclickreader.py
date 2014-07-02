from itertools import izip

class ImageClickReader:
    
    def __init__(self, inputfile):
        
        self.dffs = []
        self.xs = []
        self.ys = []
        
        for line in open(inputfile,'r'):
            dff, x, y = line.split()
            self.dffs.append(dff)
            self.xs.append(int(x))
            self.ys.append(int(y))
            
    def __iter__(self):
        
        return izip(self.dffs, self.xs, self.ys)