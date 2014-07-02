
from unittest import TestCase
from stdic import Stdic
from os import path
from os import remove

import glob
import time

class CreepExperimentTest(TestCase):
	""" XXX: refactor, not an unittest """
	
	showtimes		= True

	folder			= path.join("testsuite","test2")
	config			= path.join(folder,"test2.dicconf")

	def testCreepExperiment(self):	
		deformation = self.getDffDeformation(self.folder, self.config)
		self.assertAlmostEqual(deformation, 180.944640, 4)
		
	def getDffDeformation(self, folder, config):
		time1 = time.clock()
		experiment = Stdic(folder,folder, config)
		experiment.run()
		time2 = time.clock()
		timetaken = time2 - time1
		if self.showtimes:
			print "Time taken: %s seconds." % timetaken
		self.dffFilename	= glob.glob(path.join(self.folder,"*.dff"))[0]
		dffFile 	= open(self.dffFilename,'r')
		remove(self.dffFilename)
		for line in dffFile:
			linesplit = line.split()
			if len(linesplit) == 0:
				continue
			if linesplit[0] != '%':
				if int(linesplit[0]) == 10 and int(linesplit[1]) == 180:
					return float(linesplit[3])

