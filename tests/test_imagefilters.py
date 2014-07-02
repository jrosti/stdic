
from unittest import TestCase
from imagefilters import *

class mock_imageobject:
    
    def __init__(self, number):
        self.picturenumber = "%04d" % number
        
class mock_configsub:
    
    def __init__(self, name, configdict):
        self.configDict = dict({'name':name})
        self.configDict.update(configdict)
    
    def getValues(self):
        return self.configDict
        
class mock_configobject:
    
    def __init__(self):
        sub1 = mock_configsub('PictureNumber', dict({'firstpicturenumber':50}))
        self.subs = dict({'sub1':sub1})
    
    def getSubs(self):
        return self.subs
        
class test_imagefilters(TestCase):
    
    def _checkInstance(self, instance):
        filterclasses = [
                         picturenumberfilter.PictureNumberFilter,
                         imagefilter.TrueFilter
                         ]
        
        for filterclass in filterclasses:
            if isinstance(instance, filterclass):
                return True
        return False
    
    def testImageFilterFactory(self):
        testconfig = mock_configobject()
        
        test_factory = imagefilter.ImageFilterFactory()
        filters = test_factory.getImageFilters(testconfig)
        for filter in filters:
            self.assertTrue(self._checkInstance(filter))
        
    def test_PictureNumberFilter(self):
        
        test_filter = picturenumberfilter.PictureNumberFilter(dict({'analyzepicturenumber':0, 'firstpicturenumber':2, 'lastpicturenumber':3}))
        
        resultarray = [
                       True,
                       False,
                       True,
                       True,
                       False,
                       ]
        
        for i in xrange(0,5):
            self.assertEquals(resultarray[i], test_filter.filter(mock_imageobject(i)))