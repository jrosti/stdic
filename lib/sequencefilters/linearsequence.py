from sequencefilter import SequenceFilter
    
class LinearSequence(SequenceFilter):
    
    def __init__(self, orderer, skip=1, start=0, end=-1):
                
        self.skip = skip
        self.start = start
        self.end = end*skip
        SequenceFilter.__init__(self, orderer)
        
    def filter(self, objectlist):
        sortedlist = self.orderer.order(objectlist)
        
        if self.end <= self.start:
            self.end = len(sortedlist)

        skippedlist = []
        for index in xrange(self.start, self.end, self.skip):
            skippedlist.append(sortedlist[index])
        
        return skippedlist