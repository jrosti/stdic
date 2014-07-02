from unittest import TestCase
from imagelist import ImageList
from glob import glob
from os import path
from os import getcwd
from test_imagelist import *

class mock_sequencefilter:
    
    def __init__(self):
        pass
    
    def filter(self, list):
        return list
    
class mock_imagefilter:
    
    def __init__(self):
        pass
    
    def filter(self, file):
        return True
    
class mock_imageobject:
    
    def __init__(self, filename, regexp=None):
        self.filename = filename
        self.regexp = regexp
    
class test_imagelist(TestCase):
    
    def test_imagelist(self):
        
        cwd         = getcwd()
        test_folder = path.join(cwd, path.join('testsuite','testimages'))
        testlist    = glob(path.join(test_folder, '*.tiff'))
        
        mock_seq    = mock_sequencefilter()
        mock_img    = mock_imagefilter()
        
        imagelist = ImageList(testlist, mock_imageobject, mock_seq, [mock_img])
                            
        for image, filename in zip(iter(imagelist),iter(testlist)):
            self.assertTrue(isinstance(image, mock_imageobject))
            self.assertEquals(image.filename, filename)
            
        imagelist2 = ImageList(testlist, mock_imageobject, mock_seq, [mock_img], 'test_regexp')
                            
        for image, filename in zip(iter(imagelist2),iter(testlist)):
            self.assertTrue(isinstance(image, mock_imageobject))
            self.assertEquals(image.filename, filename)
            self.assertEquals(image.regexp, 'test_regexp')
                      
            