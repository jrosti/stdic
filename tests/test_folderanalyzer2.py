
from unittest import TestCase
from folderanalyzer2 import FolderAnalyzer
from pairiterators.tofirstiterator import ToFirstIterator
from exporters.dffexporter import DffExportParameters
from dfftools import PictureNumberDffname
from dic import Dic

class mock_dic:
    
    def analyze(self, image1, image2):
        pass
    
class mock_dffchecker:
    
    def checkExistence(self, dffname):
        return True
    
class mock_exporter:
    
    def __init__(self, image1, image2, dic, parameters, dffname):
        print image1.filename, image2.filename
    
    def export(self):
        pass

class test_folderanalyzer2(TestCase):
    
    def test_init(self):
        
        configuration = "test_folderanalyzer2.conf"
        folder = "testsuite/testimages"
        
        folderanalyzer = FolderAnalyzer(folder,folder,configuration)
        
        self.assertTrue(isinstance(folderanalyzer.pairiterator, ToFirstIterator))
        self.assertTrue(isinstance(folderanalyzer.exportparameters, DffExportParameters))
        self.assertTrue(isinstance(folderanalyzer.namegenerator, PictureNumberDffname))
        self.assertTrue(isinstance(folderanalyzer.dic, Dic))
        
    def test_analyze(self):
        
        configuration = "test_folderanalyzer2.conf"
        folder = "testsuite/testimages"
        
        folderanalyzer = FolderAnalyzer(folder,folder,configuration)
        
        folderanalyzer.dic = mock_dic()
        folderanalyzer.exporter = mock_exporter
        
        folderanalyzer.analyze()
        