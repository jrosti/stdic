from dffreader import DffReader

class CTFinderFactory:
    
    def __init__(self):
        
        from ctfolder import CTFolder
        from ctpoint import CTPoint
        
        self.ctfinders = dict({
                               "ctfolder":CTFolder,
                               "ctpoint":CTPoint
                               })
    
    def getCTFinder(self, data, criterionclass):
        
        from os.path import isdir
    
        if isdir(data):
            return self.ctfinders["ctfolder"](data,criterionclass)
        else:
            return self.ctfinders["ctpoint"](data,criterionclass)

class CTFinder:
    
    def __init__(self, dffs, criterionclass):
        
        dffreader = DffReader(dffs[0])
        
        self.dffs = dffs            
        # Stepsize is the step of the dff.
        self.step = dffreader.step
        # Shape is the shape of the original image.
        self.shape = [self.step * dffreader.defY.shape[0], self.step * dffreader.defY.shape[1]]
    
        self.criterionclass = criterionclass
    
    def getCrackTip(self, dff):
        return (0,0)
    
    def getCrackTips(self, output):
        
        # Batch script. Will analyze all dffs in the pointfile and write output to output.fcpts.
        
        outputfile = open("%s" % output, 'w')
        outputfile.close()
                      
        for index in xrange(len(self.dffs)):
            y,x = self.getCrackTip(index)
            outputfile = open("%s" % output, 'a')
            outputfile.write("%s %d %d\n" % (self.dffs[index], x, y))
            outputfile.close()