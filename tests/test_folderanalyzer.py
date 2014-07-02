from unittest import TestCase
from folderanalyzer import FolderAnalyzer
from masterdata import MasterData

import os

class test_FolderAnalyzer(TestCase):
	
	dffPath = 'newDffPath'
	
	def testInitSuccess(self):
		masterdata = MasterData()
		fa = FolderAnalyzer('.', self.dffPath, masterdata, masterdata)
		self.assertTrue(fa)
		
	def tearDown(self):
		os.rmdir(self.dffPath)
		