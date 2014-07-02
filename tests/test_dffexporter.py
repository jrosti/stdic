
import sys, os
sys.path.append(os.path.abspath("../lib/"))

import unittest
import numpy
from unittest import TestCase
from exporters.exporter import ExporterParameters
from exporters.dffexporter import DffExporter
from diccontroller import DICController

import os

class MockDeformationData:
	# XXX: mock tells us that we are VERY coupled to the deformationdata internal structure
	def __init__(self):
		self.dic = DICController()
		self.data = {"Crop" : (100,100,120,120), 
					 "PictureSize" : (100,100), 
					 "PictureData1":{"key":"in","key":"is"}, 
					 "PictureData2":{"complicated":"stuff"}, 
					 "FirstPictureName":"name1",
					 "SecondPictureName":"name2"}

		self.shape = (2,2)
		
	def get(self, key):
		return self.data[key]

	def getDeformationAtPoints(self, pointarray):
		self.getDeformationAtPointsCalled = True
		return numpy.array([[1,2],[3.4, 4.5]])
	
class MockImage:
	
	def __init__(self):
		self.__dict__ = {}

class test_DffExporter(TestCase):
	
	def setUp(self):
		self.mockdeformation = MockDeformationData()
		self.exportparameters = ExporterParameters()
		self.image = MockImage()
		# XXX: dependency from fs resource
		self.testfilename = 'test.dff'

	def testInit(self):
		exporter = DffExporter(	self.image,
								self.image,
								self.mockdeformation, 
								self.exportparameters, 
								self.testfilename)
		self.assertTrue(exporter.deformation)
		self.assertTrue(exporter.exportparameters)
		self.assertTrue(exporter.outputfilename)
		
		
	def testExportData(self):
		exporter = DffExporter(	self.image, self.image,
								self.mockdeformation, 
							   	self.exportparameters, 
							   	self.testfilename)
		self.assertTrue(exporter.export())
		self.assertTrue(self.mockdeformation.getDeformationAtPointsCalled)
		self.assertTrue(os.path.exists(self.testfilename))
		# XXX: should assert data

	def tearDown(self):
		if os.path.exists(self.testfilename):
			os.remove(self.testfilename)
			
			
			
if __name__ == '__main__':
    unittest.main()

	