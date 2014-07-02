import unittest
from stdic import Stdic
from os import path
from math import *
from glob import glob
import numpy as np

class TestPoly(unittest.TestCase):

	def test_PolynomialTransform(self):

		folder		= path.join("test_transforms","test_poly")
		config		= path.join(folder,"poly.dicconf")
		
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
		
		averages	= []
		
		coefsarray		= np.zeros((5,3,2))
		coefsarray[0]	= np.array([1.0, 0.0, 0.0, 1.0, -1.2454075596238809e-05, -2.10659363809e-05], float).reshape(3,2)
		coefsarray[1]	= np.array([1.0, 0.0, 0.0, 1.0, -2.4663953631767257e-05, -4.17188151856e-05], float).reshape(3,2)
		coefsarray[2]	= np.array([1.0, 0.0, 0.0, 1.0, -3.6636746656896907e-05, -6.19706672175e-05], float).reshape(3,2)
		coefsarray[3]	= np.array([1.0, 0.0, 0.0, 1.0, -4.8379293662312578e-05, -8.18330605565e-05], float).reshape(3,2)		
		coefsarray[4]	= np.array([1.0, 0.0, 0.0, 1.0, -5.9898173105720345e-05, -0.000101317122594], float).reshape(3,2)
		
		for i in xrange(len(dfflist)):
		
			testX		= np.zeros((dffpointsy, dffpointsx),float)
			testY		= np.zeros((dffpointsy, dffpointsx),float)
			coefs		= coefsarray[i]
			
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
			
			inverseX	= coefs[0,0]*testX + coefs[1,0]*testY + coefs[2,0]*testX*testY
			inverseY	= coefs[0,1]*testX + coefs[1,1]*testY + coefs[2,1]*testX*testY
			
			diffX		= refX - inverseX
			diffY		= refY - inverseY
			
			xerroriter	= diffX.flat
			yerroriter	= diffY.flat

			if printarrays:
				refX.tofile('refX%02d.txt' % i, '\n')
				inverseX.tofile('inverseX%02d.txt' % i, '\n')
				diffX.tofile('diffX%02d.txt' % i, '\n')
			
				refY.tofile('refY%02d.txt' % i, '\n')
				inverseY.tofile('inverseY%02d.txt' % i, '\n')
				diffY.tofile('diffY%02d.txt' % i, '\n')

			errormap	= map(hypot, xerroriter, yerroriter)
			errorarray	= np.asfarray(errormap).reshape(refX.shape)
			
			averages.append(np.average(errorarray[10:-10,5:-5]))

			errorfile	= open(path.join(folder,"errorarray%02d.txt" % i), 'w')
		
			for error in errorarray.flat:
				errorfile.write("%f\n" % error)
			errorfile.close()
		
		averagefile	= open(path.join(folder,"averages.txt"), 'w')
		for average in averages:
			averagefile.write("%f\n" % error)

