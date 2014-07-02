
from pairiterators import *
from unittest import TestCase

class mock_imagelist:
    
    def __init__(self,number):
        
        self.imagelist = xrange(number)
        
    def __iter__(self):
        self._iterator = iter(self.imagelist)
        return self
    
    def next(self):
        return self._iterator.next()
        

class test_pairiterators(TestCase):
    
    def test_PairIteratorFactory(self):
        
        imagelist = mock_imagelist(0)
        
        name1 = 'First'
        name2 = 'Previous'

        factory = pairiterator.PairIteratorFactory()
        
        iterator1 = factory.getPairIterator(name1,imagelist)
        iterator2 = factory.getPairIterator(name2,imagelist)
        
        self.assertTrue(isinstance(iterator1, tofirstiterator.ToFirstIterator))
        self.assertTrue(isinstance(iterator2, topreviousiterator.ToPreviousIterator))
        
    def test_ToFirstIterator(self):
        
        config_number = 5
        
        imagelist = mock_imagelist(config_number)
        iterator = iter(tofirstiterator.ToFirstIterator(imagelist))
        
        results = []
        for number in xrange(1,config_number):
            results.append((0,number))

        for tuple1, tuple2 in zip(results, iterator):
            self.assertEquals(tuple1, tuple2)
            
    def test_ToPreviousIterator(self):
        
        config_number = 5
        
        imagelist = mock_imagelist(config_number)
        
        iterator = iter(topreviousiterator.ToPreviousIterator(imagelist))
        
        results = []
        for number in xrange(config_number):
            results.append((number,number + 1))
        results.pop(-1)
        
        for tuple1, tuple2 in zip(results, iterator):
            self.assertEquals(tuple1, tuple2)
        