from exporter import Exporter
from numpy import save as npsave

import os
import errno

class DffExporter(Exporter):
	""" 
		Exports a deformation using single ASCII format as an output. 
	
		XXX: Describe format here.
	"""
	def __init__(	self, image1, image2, deformation, 
					exportparameters, outputfilename):
		self.image1	= image1
		self.image2 = image2
		self.deformation = deformation
		self.exportparameters = exportparameters
		self.outputfilename = outputfilename

	def initialize(self):
		pathname = os.path.dirname(self.outputfilename)
		try:
			if pathname:
				os.mkdir(pathname)
		except OSError as exc:
			if exc.errno == errno.EEXIST:
				pass
			else: raise

		self.outputfile = open(self.outputfilename, 'w')
		return True

	def writeVersion(self):
		""" Deformation file version identification """
		self.outputfile.write('% version: 2.0\n')
	
	def writeMetadata(self):
		""" Deformation metadata """
		imagedata1 = self.image1.__dict__
		imagedata2 = self.image2.__dict__
		for key in imagedata1.keys():
			self.outputfile.write("%% image1 %s : %s\n" % (key, imagedata1[key]))
			self.outputfile.write("%% image2 %s : %s\n" % (key, imagedata2[key]))
		self.outputfile.write("\n")
		for key in self.exportparameters.dicconfig:
			self.outputfile.write("%% %s: %s\n" % (key, self.exportparameters.dicconfig[key]))
		self.outputfile.write("\n")
	
	def writeDeformationData(self):
		""" deformation data """
		pointarray = []
		step = self.exportparameters.step
		for x in xrange(0, self.deformation.shape[1], step):
			for y in xrange(0, self.deformation.shape[0], step):
				pointarray.append([y,x])
		deformedpointarray = self.deformation.getDeformationAtPoints(pointarray)
		for index in xrange(0, len(pointarray)):
			x = pointarray[index][1]
			y = pointarray[index][0]
			xd = deformedpointarray[index][1]
			yd = deformedpointarray[index][0]
			self.outputfile.write("%d %d %lf %lf \n" % (x, y, xd, yd))
		
	def finalize(self):
		self.outputfile.close()
		return True
	