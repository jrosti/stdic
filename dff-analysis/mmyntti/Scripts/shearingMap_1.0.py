import sys
import os
from numpy import *
import matplotlib.pyplot as mpl
from scipy import stats as sp

# This script creates local shear maps from .dff data files. Here, shrearing
# is defined by G = eps_xy + eps_yx = (d u_x)/(d y) + (d u_y)/(d x), where
# u_x is deformation into x direction and vice versa.

class DisplayDff:
	
	def __init__( self, filenames ):
	    """
	    BEFORE USING THIS SCRIPT, RUN xAnalysis.py WITH YOUR SAMPLES TO GET SCALES!
	    """

            self.lag = 1	# A constant used in numeric derivating.
            self.stepy = None	# Distance between the data points in DIC:ing 
				# (read in dff in readData)

            for fn in filenames:

                print "Shear map for " + fn

                diffX, diffY, deltat, name, width, heigth, time = self.readData(fn)

	        # Getting scale, scaled height and width (in millimeters) and the ratio
		# of the height and width. Putting them inside the loop ensures that if
		# multiple samples are analyzed, each of them uses its own scale.
	        scale = self.lookForScale(name)

                epsXY = ( diffX[:,self.lag:] - diffX[:,:-self.lag] )/( self.lag*self.stepy )
                epsYX = ( diffY[:,self.lag:] - diffY[:,:-self.lag] )/( self.lag*self.stepy )
		shearing = epsXY + epsYX

                (x,y) = shearing.shape
		x1 = int(ceil(x/4))		# Crops 1/4 away from each side
		x2 = x-x1			# in x direction.
		vCutSY = mean(shearing[x1:x2,:],0)	# Average strain.
                yp = arange(0,y)*self.stepy		# Y vector for locating each shearing point, as pixels.
		xp = arange(0,x)*self.stepy		# X vector for locating each shearing point, as pixels.
		mmDepth = [0] * len(yp)			# Y as millimeters
		mmWidth = [0] * len(xp)			# X as millimeters

		for i in range(len(yp)):
			mmDepth[i] = float(yp[i]) * scale

		for i in range(len(xp)):
			mmWidth[i] = float(xp[i]) * scale

		ratio = mmWidth[-1]/mmDepth[-1]

		# SHEAR MAP

		axissize=(0.5*(1-0.60*ratio)+0.05,0.2,0.60*ratio,0.60)

		fig=mpl.figure(num=2,figsize=(6,5),facecolor='w',edgecolor='k')
		mpl.clf() # If this is commented, every second picture turns upside-down...?
		ax=fig.add_axes(axissize)
		mpl.contourf(mmWidth, mmDepth, shearing.T * 100,50) # Into percents
                mpl.gca().invert_yaxis()
                locs, labels = mpl.yticks(fontsize=9)
                locs, labels = mpl.xticks(fontsize=9)

		mpl.axis('tight')
		mpl.xlabel("Width [mm]", fontsize=12)
		mpl.ylabel("Depth from non-fatigued side [mm]", fontsize=12)
		mpl.colorbar() # Colorbar
                savefn = fn.split('.dff')[0] + "-shearmap.pdf"
              	mpl.savefig(savefn, dpi=300, facecolor='w', edgecolor='w',
			    orientation='portrait', format='pdf',
			    transparent=True, bbox_inches=None, pad_inches=0.1) 

            
	def readData(self, filename):
            """
            Reads dff to matrices: u,v (x-disp and y-disp), also deltat, name of the sample,
	    width of the sample and height of the sample, and the time number of the sample.
            """
            # read raw data
            dff = open(filename,'r')
            dfflines = dff.readlines()
            dff.close()
            
            # find spatial coordinates
            lastline = dfflines[len(dfflines)-1]
            lastlinesplit = lastline.split()
            
            last_x	= int(lastlinesplit[0]) # Same as width in pixels.
            last_y	= int(lastlinesplit[1])	# Same as height in pixels.
            
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
            
            testX		= zeros((dffpointsx, dffpointsy),float)
            testY		= zeros((dffpointsx, dffpointsy),float)
            
            # get time difference between pictures
            time1 = dfflines[3].split('-0000-')[1].split('-8bit')[0]
            time2 = dfflines[4].split('-0000-')[1].split('-8bit')[0]
            deltat = float(time2) - float(time1)
		
	    # Getting the name and the time stamp of the sample
	    nameData = dfflines[3].split("/")
	    nameDataLen = len(nameData)
	    nameRaw = nameData[nameDataLen - 3]
	    name = nameRaw.split("_skip_")[0]

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
                
		xgrid		= arange(0,dffpointsx)
		ygrid		= arange(0,dffpointsy)
		refX, refY	= meshgrid(ygrid, xgrid)
                
		diffX		= testX		# The movements of the points in x direction.
		diffY		= testY		# The movements of the points in y direction.
		
            return diffX, diffY, deltat, name, last_x, last_y, float(time1)



	def lookForScale(self, name):

	    # Looking for the scale. Should be fixed for more useful format...
	    width = open("/home/mmyntti/Scripteja/xResults.csv",'r')
	    widthData = width.readlines()
	    width.close()

	    scale = 1.0 	# If the real scale can't be found, the script 
	    			# doesn't scale at all but keeps the original
				# pixel measurements. You'll notice if it happens.
		
	    for i in range(len(widthData)):
		widthSplitData = widthData[i-1].split(", ")
		if name in widthSplitData:
		    scale = float(widthSplitData[1].strip())
		else:
		    continue

	    return scale
            
if __name__=="__main__":
	
    if len(sys.argv) == 0:
        print "usage: shearingMap_1.0.py <dff-files>"
        print "       python plotdff.py file1.dff file2.dff"
        sys.exit()

    plot = DisplayDff(sys.argv[1:])
