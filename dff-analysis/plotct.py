import sys
import numpy as np
import matplotlib.pyplot as mpl
from dffreader import DffReader
from crackangle import CrackAngle

class PlotCT:

	def __init__(self, filename, x, y):
					
		reader = DffReader(filename)
		self.diffX = reader.defX - reader.origX
		self.diffY = reader.defY - reader.origY
		self.x = x
		self.y = y
		self.crackangle = CrackAngle(filename)
				
	def plotCrack(self):
		
		fig = mpl.figure()
		ax = fig.add_subplot(111)
			
		diffY = self.diffY
		
		mpl.contourf(diffY,50)
		mpl.axis("tight")
		mpl.xlabel("Y-displacement")
		mpl.colorbar()
		mpl.gca().invert_yaxis()
		
		self.crackangle.setCoords(self.x,self.y,45)
		
		xcoords = self.crackangle.xcoords
		ycoords = self.crackangle.ycoords
		step = self.crackangle.step
		
		ax.plot(xcoords[::step], ycoords[::step], '-', color='k')
		
		self.crackangle.setCoords(self.x,self.y,-45)
		xcoords = self.crackangle.xcoords
		ycoords = self.crackangle.ycoords
		step = self.crackangle.step
		
		ax.plot(xcoords[::step], ycoords[::step], '-', color='k')
		
		#Plot of Eyy
		
		fig = mpl.figure()
		ax = fig.add_subplot(111)
		
		mpl.hold(True)
		
		derY = np.diff(self.diffY, 1, 0)
		
		mpl.contourf(derY,50)
		mpl.axis("tight")
		mpl.xlabel("Eyy")
		mpl.colorbar()
		mpl.gca().invert_yaxis()
		
		self.crackangle.setCoords(self.x,self.y,45)
		
		xcoords = self.crackangle.xcoords
		ycoords = self.crackangle.ycoords
		step = self.crackangle.step
		
		ax.plot(xcoords[::step], ycoords[::step], '-', color='k')
		
		self.crackangle.setCoords(self.x,self.y,-45)
		xcoords = self.crackangle.xcoords
		ycoords = self.crackangle.ycoords
		step = self.crackangle.step
		
		ax.plot(xcoords[::step], ycoords[::step], '-', color='k')
		
		mpl.show()

if __name__ == "__main__":
	pointfile = open(sys.argv[1],'r')
	for line in pointfile:
		filename, x, y = line.split()
		tipPlots = PlotCT(filename, float(x), float(y))
		tipPlots.plotCrack()
		
#------------------------------------------------------------------------------

