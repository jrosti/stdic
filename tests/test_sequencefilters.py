
from unittest import TestCase
from sequencefilters import *
from itertools import izip

class mock_orderer:

    def order(self, imagelist):
        return imagelist

class test_sequencefilters(TestCase):
    
    def testSequenceFilterFactory(self):
        test_factory = sequencefilter.SequenceFilterFactory()
        orderer = mock_orderer()
        
        config1 = ["Linear", orderer]
        
        filter1 = test_factory.getSequenceFilter(*config1)
        
        self.assertTrue(isinstance(filter1, linearsequence.LinearSequence))
        
    def test_LinearSequence(self):
        
        orderer = mock_orderer()
        configs = [
            dict(skip=1),
            dict(skip=2),
            dict(start=1),
            dict(end=9),
            dict(start=1, end=9),
            dict(start=1, end=9, skip=3),
        ]
        
        numberlist = range(10)
        results = [
                   range(10),
                   range(0,10,2),
                   range(1,10),
                   range(0,9),
                   range(1,9),
                   range(1,9,3),
                   ]
        
        for config,result in izip(configs, results):
            test_sequence = linearsequence.LinearSequence(orderer, **config)
            self.assertEquals(test_sequence.filter(numberlist), result)
