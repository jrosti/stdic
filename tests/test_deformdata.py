
from os import path
from configparser import ConfigParser
from masterdata import MasterData
from unittest import TestCase
import deformdata  
import glob
import time

class DeformDataTest(TestCase):
	""" XXX: not an unit test, since testes actual deformations """
	showtimes		= False
	rootfolder		= "testsuite"

	folder1			= path.join(rootfolder, "test1")
	filename1		= "*.tiff"
	config1			= path.join(folder1,"test1.dicconf")
	config1crop		= path.join(folder1,"test1crop.dicconf")

	folder2			= path.join(rootfolder, "test2")
	filename2		= "*.tiff"
	config2			= path.join(folder2,"test2.dicconf")
	
	folder3			= path.join(rootfolder, "test3")
	filename3		= "*.png"
	config3			= path.join(folder3,"test3.dicconf")




	def testDeformData1(self):
	
		deformation = self.getDeformation(self.folder1, self.filename1, self.config1)
		self.assertAlmostEqual(deformation, 180.970526, 4)
		
	def testDeformData1cropped(self):
			
		deformation = self.getDeformation(self.folder1, self.filename1, self.config1crop)
		self.assertAlmostEqual(deformation, 180.893970, 4)

	def testDeformData2(self):
			
		deformation = self.getDeformation(self.folder2, self.filename2, self.config2)
		self.assertAlmostEqual(deformation, 180.944640, 4)

	def testDeformData3(self):
			
		deformation = self.getDeformation(self.folder3, self.filename3, self.config3)
		self.assertAlmostEqual(deformation, 180.708853, 4)

	def getDeformation(self, folder, filename, config):
		pictures = glob.glob(path.join(folder, "%s" % filename))
		pictures.sort()
		configdata = MasterData()
		ConfigParser(config, configdata, 'deformdata.py').parse()
		time1 = time.clock()
		defData = deformdata.DeformationData(pictures[0], pictures[1], configdata)
		time2 = time.clock()
		timetaken = time2 - time1
		if self.showtimes:
			print "Time taken: %s seconds." % timetaken
		deformation = defData.getDeformationAtPoints([(10,180)])
		return deformation[0][1]
