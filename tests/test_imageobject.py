from unittest import TestCase
from imageobject import ImageObject
from os import getcwd
from os import path

class test_ImageObject(TestCase):
    
    def test_init(self):
        
        folder = path.join(path.join(getcwd(), 'testsuite'), 'test_imageobject')
        
        imagefile = path.join(folder, 'test-parameter1-parameter2-1000.tiff')
      
        imageobject = ImageObject(imagefile)
        
        from PIL.TiffImagePlugin import TiffImageFile
        
        self.assertTrue(isinstance(imageobject.getImage(), TiffImageFile))
        
    def test_properties(self):
       
        folder = path.join(path.join(getcwd(), 'testsuite'), 'test_imageobject')
        
        imagefile = path.join(folder, 'test-parameter1-parameter2-1000.tiff')
      
        imageobject = ImageObject(imagefile, '^.*-(?P<key1>\w+)-(?P<key2>\w+)-(?P<picturenumber>\d+)\.tiff$')
        
        resultdictionary = dict({'filename':imagefile, 'key1':'parameter1', 'key2':'parameter2', 'picturenumber':'1000'})
        
        for key in resultdictionary:
            self.assertEquals(getattr(imageobject,key), resultdictionary[key])