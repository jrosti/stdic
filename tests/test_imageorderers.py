
from unittest import TestCase
from sequencefilters import *
from random import shuffle

class mock_imageobject:
    
    def __init__(self, number):
        self.filename = 'name%d' % number
        self.picturenumber = number

class test_imageorderers(TestCase):
    
    def testImageOrderFactory(self):
        test_factory = imageorder.ImageOrderFactory()
        
        config1 = "PictureNumber"
        config2 = "Filename"
        
        order1 = test_factory.getImageOrder(config1)
        order2 = test_factory.getImageOrder(config2)
        
        self.assertTrue(isinstance(order1, picturenumberorder.PictureNumberOrder))
        self.assertTrue(isinstance(order2, filenameorder.FilenameOrder))
        
    def _generateRandomImageList(self, numberrange):
        
        
        imagelist = []
        for number in numberrange:
            imagelist.append(mock_imageobject(number))
        
        shuffle(imagelist)
        
        return imagelist
        
        
    def test_PictureNumberOrder(self):
        
        test_order = picturenumberorder.PictureNumberOrder()
        
        numberrange = range(1,10)
        
        randomlist = self._generateRandomImageList(numberrange)
                
        orderedlist = test_order.order(randomlist)
        
        for number, image in zip(numberrange, orderedlist):
            self.assertEquals(number, image.picturenumber)
        
        
    def test_FilenameOrder(self):
        
        test_order = filenameorder.FilenameOrder()
        
        numberrange = range(1,10)
        
        randomlist = self._generateRandomImageList(numberrange)
                
        orderedlist = test_order.order(randomlist)
        
        for number, image in zip(numberrange, orderedlist):
            self.assertEquals('name%d' % number, image.filename)
        
        