from pairiterator import PairIterator
from itertools import tee

class ToPreviousIterator(PairIterator):

    def __init__(self, imagelistobject):
        PairIterator.__init__(self, imagelistobject)
        
    def next(self):
        return (self._listiterator1.next(), self._listiterator2.next())
        
    def __iter__(self):
        self._listiterator1, self._listiterator2 = tee(iter(self.imagelist),2)
        self._listiterator2.next()
        return self