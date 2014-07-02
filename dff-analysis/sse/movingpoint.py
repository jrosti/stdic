import sys
import os
from glob import glob
import numpy as np
import scipy.interpolate as sp
import matplotlib.pyplot as mpl

class DffAnalysis:

	def __init__(	self, dffDir, rawDir, datPath, x, y   ):

		self.stepy = None
		self.lag = 10   # Lag for numerical derivative
		self.x = int(x) #38
		self.y = int(y) #47
		
		# Read in paths to the .dff and .png files
		dffFiles = glob( dffDir + "/*.dff" )
		dffFiles.sort()

		strainY = np.zeros( len(dffFiles), float )

		# Process strainY
		i = 0
		while i < len(dffFiles):
			filename = dffFiles[i]
			print filename
			diffX, diffY = self.readData(filename)
			strainY[i] = self.evalStrainY( self.x,
						       self.y,
						       diffY )
			newx = self.x + 0.1*self.evalDiff( self.x,
							   self.y,
							   diffX )
			newy = self.y + 0.1*self.evalDiff( self.x,
							   self.y,
							   diffY )

			# For testing how moving of x and y works
			#mpl.figure(1)
			#mpl.clf()
			#img = mpl.imread(imgFiles[i])
			#mpl.imshow(img,cmap=mpl.cm.gray)
			#mpl.plot(10*self.x, 10*self.y, 'ko', markersize=5)
			#savestring = 'jpg/%d.jpg' % i
			#mpl.savefig(savestring)

			self.x = newx
			self.y = newy
			i = i + 1
		
		# Save data
		np.savetxt(datPath, strainY, fmt='%1.4e')


	def evalDiff(self, x, y, diff):

		imin = int(x) - 5
		imax = imin + 10
		jmin = int(y) - 5
		jmax = jmin + 10

		if jmin < 0:
			return 0
		if jmax > len(diff[1,:]):
			return 0

		xticks = np.arange(0,len(diff[:,1]))
		yticks = np.arange(0,len(diff[1,:]))
		ygrid, xgrid = np.meshgrid(yticks,xticks)

		xgrid = xgrid[imin:imax,jmin:jmax]
		ygrid = ygrid[imin:imax,jmin:jmax]
		diff  = diff[imin:imax,jmin:jmax]

		print xgrid.shape
		print ygrid.shape
		print diff.shape

		diffAt = sp.interp2d(xgrid, ygrid, diff, kind='linear')
		return diffAt(x,y)

	def evalStrainY(self, x, y, diff):

		imin = int(x) - 5
		imax = imin + 10
		jmin = int(y) - 5
		jmax = jmin + 10

		if jmin < 0:
			return 0
		if jmax > len(diff[1,:]):
			return 0

		xticks = np.arange(0,len(diff[:,1]))
		yticks = np.arange(0,len(diff[1,:]))
		yticks = yticks[self.lag:]
		ygrid, xgrid = np.meshgrid(yticks,xticks)

		strainY = (diff[:,self.lag:] - diff[:,:-self.lag])/(self.lag*self.stepy)
		
		xgrid = xgrid[imin:imax,jmin:jmax]
		ygrid = ygrid[imin:imax,jmin:jmax]
		strainY  = strainY[imin:imax,jmin:jmax]

		strainAt = sp.interp2d(xgrid, ygrid, strainY, kind='linear')

		return strainAt(x,y)


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
		
		return (diffX, diffY)
		
		
			

if __name__=="__main__":
	
	if len(sys.argv) < 1:
		print "usage: "
		print "       "
		sys.exit()

	plot = DffAnalysis( sys.argv[1],
			    sys.argv[2],
			    sys.argv[3],
    			    sys.argv[4],
			    sys.argv[5] )
