
import numpy as np

class DffReader:

	def __init__(self, filename):
	
		self.filename = filename
			
		dff = open(self.filename,'r')
		
		dfflines = dff.readlines()
		
		dff.close()
		
		lastline = dfflines[len(dfflines)-1]
		lastlinesplit = lastline.split()
		
		last_x	= int(lastlinesplit[0])
		last_y	= int(lastlinesplit[1])
		
		lastline2 = dfflines[len(dfflines)-2]
		lastlinesplit2 = lastline2.split()
		
		last2_y	= int(lastlinesplit2[1])
		
		self.step = last_y - last2_y
		
		dffpointsx	= (last_x + self.step)/self.step
		dffpointsy	= (last_y + self.step)/self.step
				
		self.origX		= np.zeros((dffpointsy, dffpointsx),float)
		self.origY		= np.zeros((dffpointsy, dffpointsx),float)
				
		self.defX		= np.zeros((dffpointsy, dffpointsx),float)
		self.defY		= np.zeros((dffpointsy, dffpointsx),float)
		
		for line in dfflines:
			linesplit = line.split()
			try:
				x	= int(linesplit[0])
				y	= int(linesplit[1])
				dx	= float(linesplit[2])
				dy	= float(linesplit[3])
			except (ValueError, IndexError):
				continue
				
			xcoord = x/self.step
			ycoord = y/self.step
			self.origX[ycoord,xcoord]	= x
			self.origY[ycoord,xcoord]	= y
			self.defX[ycoord,xcoord]	= dx
			self.defY[ycoord,xcoord]	= dy
