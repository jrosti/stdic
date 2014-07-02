import numpy as np
import sys
from math import *
from dffreader import DffReader
from scipy.ndimage.interpolation import map_coordinates

class CrackPoint:

	def __init__(self, filename):
	
		dff = DffReader(filename)
	
		self.origs = dff.getOrigs()
		self.defs = dff.getDefs()
		
		self.diffs = (self.defs[0] - self.origs[0], self.defs[0] - self.origs[0])
		self.step = dff.getStep()
		
	def getE(self, axis, xcoord, ycoord, angle):
	
		derarray = np.diff(self.diffs[axis], 1, axis)
		
		xcoord = xcoord/self.step
		ycoord = ycoord/self.step
	
		angle = radians(angle)
	
		xcoords = np.array([], dtype=float)
		ycoords = np.array([], dtype=float)
		
		xcoordplus	= cos(angle)/self.step
		ycoordplus	= - sin(angle)/self.step
		maxX		= derarray.shape[1] - 1
		maxY		= derarray.shape[0] - 1
		
		while True:
			if xcoord < 0 or xcoord >= maxX or ycoord <= 0 or ycoord >= maxY:
				break
			xcoords = np.append(xcoords, xcoord)
			ycoords = np.append(ycoords, ycoord)
			
			xcoord += xcoordplus
			ycoord += ycoordplus
		
		return map_coordinates(derarray, [ycoords, xcoords], order=3)
						
	def plot(self, array):
	
		import matplotlib.pyplot as mpl
		
		mpl.figure
		mpl.contourf(array,50)
		mpl.axis("image")
		mpl.colorbar()
		mpl.gca().invert_yaxis()
		mpl.show()
				
	def plotE(self, rarray, ratio=0.25):
	
		import matplotlib.pyplot as mpl
		
		interval = (10,len(rarray)*ratio)
		#interval = (200,350)
		
		raxis	= np.arange(0, rarray.shape[0])[interval[0]:interval[1]]
		rarray	= rarray[interval[0]:interval[1]]
		
		mpl.figure
		
		mpl.subplot(2,1,1)
		mpl.plot(raxis, rarray)
		mpl.axis("tight")
	
		rarray = np.log(rarray)
		
		raxis = np.log(raxis)
		
		mpl.subplot(2,1,2)
		mpl.plot(raxis, rarray)
		
		coefs = np.polyfit(raxis,rarray,1)
		
		mpl.hold(True)
		mpl.plot(raxis, coefs[0]*raxis + coefs[1], label='slope %f' % coefs[0])
		
		mpl.axis("tight")
		mpl.legend()
		mpl.show()
				
	def plotAnglesLog(self, axis, xcoord, ycoord):
	
		import matplotlib.pyplot as mpl
		
		for angle in xrange(-45,46,15):

			rarray	= self.getE(axis, xcoord, ycoord, angle)
			raxis	= np.arange(0, rarray.shape[0])
			
			rarray = rarray[0:50]
			raxis = raxis[0:50]

			mpl.figure(1)
			mpl.plot(raxis, rarray, label='angle %d' % angle)
			mpl.legend()
			
			mpl.axis("tight")
			mpl.hold(True)
			coefs = np.polyfit(np.log(raxis),np.log(rarray),1)

			mpl.figure(2)
			mpl.plot(np.log(raxis), np.log(rarray),'o')
			mpl.hold(True)
			mpl.plot(np.log(raxis), coefs[0]*np.log(raxis) + coefs[1], label='angle: %d slope: %f' % (angle, coefs[0]))
			mpl.legend()

			mpl.figure(3)
			mpl.plot(angle, coefs[0], 's', label='value %f' % coefs[0])
			mpl.axis("tight")
			mpl.figure(4)
			mpl.plot(angle, coefs[1], 'o', label='value %f' % coefs[1])
			#mpl.legend()
			
			mpl.axis("tight")
			mpl.hold(True)
			
		mpl.show()
		
	def plotAngles(self, axis, xcoord, ycoord):
	
		import matplotlib.pyplot as mpl
		
		mpl.figure
		
		for angle in xrange(-90, 90, 15):
			rarray	= self.getE(axis, xcoord, ycoord, angle)
			raxis	= np.arange(0, rarray.shape[0])
			mpl.plot(raxis, rarray, label='angle %d' % angle)
			mpl.legend()
			mpl.hold(True)
		mpl.axis("tight")
		
		mpl.show()
		
if __name__=="__main__":

	filename	= sys.argv[1]
	axis		= int(sys.argv[2])
	xcoord		= float(sys.argv[3])
	ycoord		= float(sys.argv[4])
	#angle		= float(sys.argv[5])
	ratio		= 1
	
	crack = CrackPoint(filename)
	crack.plotAnglesLog(axis, xcoord, ycoord)
	#E = crack.getE(axis, xcoord, ycoord, angle)
	#crack.plotE(E, ratio)
	
