import sys
import os
from glob import glob
import numpy as np
import matplotlib.pyplot as mpl

class SliceDff:

	def __init__(   self, 
			dffDir):

		self.stepy = None
		self.dffDir  = dffDir
		self.lag = 10


		# Read in paths to the .dff files
		dffFiles = glob( dffDir + "/*.dff" )
		dffFiles.sort()

		i = 0
		while i < len(dffFiles):
			dffFile = dffFiles[i]
			diffX, diffY, deltat = self.readData(dffFile)
			# An approximate derivate with forward difference
			strainYY = ( diffY[:,self.lag:] - diffY[:,:-self.lag] )/( self.lag*self.stepy*deltat )
			(x,y) = strainYY.shape
			x1 = int(np.ceil(x/4))
			x2 = x-x1
			avgCutSYY = np.mean(strainYY[x1:x2,:],0)
			# Y-coordinates corresponding the derivative values are
			y = np.arange(self.lag,y+self.lag)*10
			# Save to file
			out = np.array(zip(y, avgCutSYY), dtype=[('int', int),('float', float)])
			outFile = dffFile + '_avgslice.dat'
			np.savetxt(outFile, out, fmt='%i, %f')
			# Plot StrainYY vs y
			mpl.figure(1)
			mpl.clf()
			mpl.plot(y,avgCutSYY)
			mpl.xlim(100,y)
			mpl.ylim(-0.02,0.002)
			outFig = dffFile + '_avgslice.png'
			mpl.savefig(outFig)
			i = i + 1
			

	def readData(self, filename):
		"""
			Reads dff to matrices: u,v (x-disp and y-disp)
		"""
		# read raw data
		dff = open(filename,'r')
		dfflines = dff.readlines()
		dff.close()
		
		# find spatial coordinates
		lastline = dfflines[len(dfflines)-1]
		lastlinesplit = lastline.split()
		
		last_x	= int(lastlinesplit[0])
		last_y	= int(lastlinesplit[1])
		
		# find step size
		# assume same step size
		# use last two lines
		lastline2 = dfflines[len(dfflines)-2]
		lastlinesplit2 = lastline2.split()
		last2_y	= int(lastlinesplit2[1])
		step = last_y - last2_y
		self.stepy = step
		
		# get number of points using stepsize
		dffpointsx	= (last_x + step)/step
		dffpointsy	= (last_y + step)/step
				
		testX		= np.zeros((dffpointsx, dffpointsy),float)
		testY		= np.zeros((dffpointsx, dffpointsy),float)

		# get time difference between pictures
		#(line.split('-0000-'))[1].split('-8bit')[0]

		time1 = dfflines[3].split('-0000-')[1].split('-8bit')[0]
		time2 = dfflines[4].split('-0000-')[1].split('-8bit')[0]
		deltat = float(time2) - float(time1)
		
		# parse the data
		for line in dfflines:
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
			testX[xcoord,ycoord]	= dx - x
			testY[xcoord,ycoord]	= dy - y
			
		xgrid		= np.arange(0,dffpointsx)
		ygrid		= np.arange(0,dffpointsy)
		refX, refY	= np.meshgrid(ygrid, xgrid)
			
		diffX		= testX
		diffY		= testY
		
		return (diffX, diffY, deltat)
		
		
			

if __name__=="__main__":
	
	if len(sys.argv) < 2:
		print "usage: strain rate vs y extractor, see __init__ for details"
		print "       python slice.py dffDir"
		sys.exit()
	
	slicedff = SliceDff(dffDir = sys.argv[1])
