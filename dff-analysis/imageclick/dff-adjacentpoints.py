from itertools import izip
from re import compile
import sys
from os import path

class PointTransformer:
    
    def __init__(self, pointfile):

        pointfile = open(pointfile,'r')
        self.dfflist = []
        self.pointlist = []
        for line in pointfile:
            linesplit = line.split()
            self.dfflist.append(linesplit[0])
            self.pointlist.append([float(linesplit[1]), float(linesplit[2])])
        
    def writeFile(self, filename, interval):
        
        outputfile = open(filename, 'w')
        
        rexpression = "^(.*)-([0]+)(\d+)-([0]+)(\d+)\.dff$"
        rexcompiled = compile(rexpression)
        for dff, points in izip(self.dfflist, self.pointlist):
            pathname, basename = path.split(dff)
            matchobject = rexcompiled.match(basename)
            prefix      = matchobject.group(1)
            zeroes1     = matchobject.group(2)
            dffnumber1  = int(matchobject.group(3))
            zeroes2     = matchobject.group(4)
            dffnumber2  = int(matchobject.group(5))
            for i in xrange(-interval,interval+1):
                newbasename = "%s-%s%d-%s%d.dff" % (prefix, zeroes1, dffnumber1 + i, zeroes2, dffnumber2 + i)
                newdff = path.join(pathname,newbasename)
                outputfile.write("%s %f %f\n" % (newdff, points[0], points[1]))

            
if __name__=="__main__":
    transformer = PointTransformer(sys.argv[1])
    transformer.writeFile(sys.argv[2], int(sys.argv[3]))