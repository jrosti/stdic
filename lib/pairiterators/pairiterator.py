      
class PairIterator:
    
    def __init__(self, imagelistobject):
        self.imagelist = imagelistobject
        

class PairIteratorFactory:
    
    def __init__(self):
    
        from tofirstiterator import ToFirstIterator
        from topreviousiterator import ToPreviousIterator
        self.PairIteratorDictionary = dict({
                                     "First":ToFirstIterator,
                                     "Previous":ToPreviousIterator,
                                     })

    def getPairIterator(self, name, imagelistobject, configdict=dict()):
        return self.PairIteratorDictionary[name](imagelistobject, **configdict)