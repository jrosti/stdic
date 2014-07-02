import sys
import numpy as np
#import matplotlib
#matplotlib.use('MacOSX')
import matplotlib.pyplot as mpl

class PlotDff:
	
	def __init__(self, filename, 
				saveString	= None, 
				datString 	= None, 
				rawImage	= None):
		
		self.filename 	= filename
		self.saveString = saveString
		self.datString  = datString
		self.rawImage   = rawImage
			
		self.diffX, self.diffY = self.readData(filename)

		lag = 1
		
		self.strainYY = self.diffY[:,lag:] - self.diffY[:,:-lag]
		self.strainXX = self.diffY[lag:,:] - self.diffY[:-lag,:]
	
	def run(self):
		
		self.plotDisplStrain(self.diffX,
					  	self.diffY,
					  	self.strainXX,
					  	self.strainYY,
					  	self.filename,
					  	self.saveString,
					  	self.rawImage)
		
	def plotDisplStrain(self, diffX, diffY, strainXX, strainYY, filename, savestring, rawImage):
		"""
			plots u and v (diffX and diffY retruned by readData) as contourplots.
		"""
		mpl.figure(1)
		mpl.suptitle(filename.split('/')[-1])

		#plotScaleMin = -5
		#plotScaleMax =  25
		#plotTicks	= [-5,-4,-3,-2,-1,0,1]
		#plotTicks	= [-25,-20,-15,-10,-5,0,5]
		#plotTicks	= map(lambda x: x*plotScaleMax,plotTicks)

		
		mpl.subplot(2,2,1)
		diffX2 = diffX
		mpl.contourf(diffX.T,50) #,vmin=plotScaleMin,vmax=plotScaleMax)
		#mpl.clim(plotScaleMin,plotScaleMax)
		#c = mpl.colorbar(ticks = plotTicks)	
		mpl.axis("image")
		mpl.xlabel("X-directional displacement")
		#mpl.colorbar()
		mpl.gca().invert_yaxis()
	
			
		mpl.subplot(2,2,2)
		diffY2 = diffY
		#diffY2[diffY >= plotScaleMax] = plotScaleMax
		#diffY2[diffY <= plotScaleMin] = plotScaleMin
		#diffY2[0,0] = plotScaleMax
		#diffY2[0,1] = plotScaleMin
		mpl.contourf(diffY.T,50) #,vmin=plotScaleMin,vmax=plotScaleMax)
		#mpl.clim(plotScaleMin,plotScaleMax)
		#c = mpl.colorbar(ticks = plotTicks)	
		mpl.axis("image")
		mpl.xlabel("Y-directional displacement")
 			#mpl.colorbar()
		mpl.gca().invert_yaxis()

		mpl.subplot(2,2,3)
		#img = mpl.imread(rawImage)
		#mpl.imshow(img,cmap=mpl.cm.gray)

		mpl.subplot(2,2,3)
		#strainXX2 = strainXX
		#strainXX2[strainXX >= plotScaleMax] = plotScaleMax
		#strainXX2[strainXX <= plotScaleMin] = plotScaleMin
		#strainXX2[0,0] = plotScaleMin
		#strainXX2[0,1] = plotScaleMax
		mpl.contourf(strainXX.T,50) #,vmin=plotScaleMin,vmax=plotScaleMax)
		#mpl.clim(plotScaleMin,plotScaleMax)		
		#c = mpl.colorbar(ticks = plotTicks)
		#mpl.axis("image")
		#mpl.xlabel("X-directional strain")
		mpl.gca().invert_yaxis()		

		mpl.subplot(2,2,4)
		strainYY2 = strainYY
		#strainYY2[strainYY >= plotScaleMax ] = plotScaleMax
		#strainYY2[strainYY <= plotScaleMin ] = plotScaleMin
		#strainYY2[0,0] = plotScaleMin
		#strainYY2[0,1] = plotScaleMax
		mpl.contourf(strainYY.T,50) #,vmin=plotScaleMin,vmax=plotScaleMax)
		#mpl.clim(plotScaleMin,plotScaleMax)		
		#c = mpl.colorbar(ticks = plotTicks)	
		mpl.axis("image")
		mpl.xlabel("Y-directional strain")
		mpl.gca().invert_yaxis()		
		
		if savestring == None:
			mpl.show()
		else:
			mpl.figure(1)
			mpl.savefig(savestring)
	
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
	
	if len(sys.argv) < 4:
		print "usage: dff-plotter, see __init__ for details"
		print "	   python plotdff.py file.dff saveFilename.jpg saveDatFilename.dat rawImageName"
		sys.exit()
	
	plot = PlotDff(sys.argv[1], saveString =  sys.argv[2], datString = sys.argv[3], rawImage = None)
	plot.run()
