import unittest
from stdic import Stdic
from os import path
from math import *
from glob import glob
import numpy as np

class TestAT(unittest.TestCase):

	def testAffineTransform(self):
	
		folder		= path.join("test_transforms","test_at")
		config		= path.join(folder,"at.dicconf")
		
		analyze		= True
		
		printarrays	= False
		
		dffpointsx	= 25
		dffpointsy	= 75
		step		= 10
		
		if analyze:
			Stdic(folder, folder, config)
		
		dfflist = glob(path.join(folder, "*.dff"))
		dfflist.sort()
		
		xgrid		= np.arange(0,dffpointsx*step,step)
		ygrid		= np.arange(0,dffpointsy*step,step)
		refX, refY	= np.meshgrid(xgrid, ygrid)
		
		for i in xrange(len(dfflist)):
		
			testX		= np.zeros((dffpointsy, dffpointsx),float)
			testY		= np.zeros((dffpointsy, dffpointsx),float)
			strain		= (i + 1)/100.0 + 1
			coefs		= np.array([1, 0, 0, strain]).reshape(2,2)
			
			dff = open(dfflist[i],'r')
		
			for line in dff:
				linesplit = line.split()
				try:
					x	= int(linesplit[0])
					y	= int(linesplit[1])
					dx	= float(linesplit[2])
					dy	= float(linesplit[3])
				except (ValueError, IndexError):
					continue
				
				xcoord = x/step
				ycoord = y/step
				testX[ycoord,xcoord]	= dx
				testY[ycoord,xcoord]	= dy
				
			deformedX	= coefs[0,0]*refX + coefs[0,1]*refY
			deformedY	= coefs[1,0]*refX + coefs[1,1]*refY

			diffX		= deformedX - testX
			diffY		= deformedY - testY
			
			xerroriter	= diffX.flat
			yerroriter	= diffY.flat
			
			if printarrays:
				deformedX.tofile('deformedX%02d.txt' % i, '\n')
				testX.tofile('testX%02d.txt' % i, '\n')
				diffX.tofile('diffX%02d.txt' % i, '\n')
				
				deformedY.tofile('deformedY%02d.txt' % i, '\n')
				testY.tofile('testY%02d.txt' % i, '\n')
				diffY.tofile('diffY%02d.txt' % i, '\n')

			errormap	= map(hypot, xerroriter, yerroriter)
			errorarray	= np.asfarray(errormap)

			errorfile	= open(path.join(folder,"errorarray%02d.txt" % i), 'w')
		
			for error in errorarray.flat:
				errorfile.write("%f\n" % error)
			errorfile.close()
