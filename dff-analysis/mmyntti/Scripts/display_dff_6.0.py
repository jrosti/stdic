import sys
import os
import numpy as np
import matplotlib.pyplot as mpl
from scipy import stats as sp

# This script is made for creating strain maps from .dff files. Strain is defined
# by S = eps_yy = (d u_y) / (d y)

class DisplayDff:
	
	def __init__( self, filenames ):
	    """
	    BEFORE USING THIS SCRIPT, RUN xAnalysis.py WITH YOUR SAMPLES TO GET SCALES!
	    """

            self.lag = 1	# A constant used in numeric derivating.
            self.stepy = None	# Distance between the data points in DIC:ing 
				# (read in dff in readData, usually 10 pixels)

            # first find max values for plotting
            print "searching for maximum and minimum strain..."
            smax = [ 0 ] * len(filenames)	# Maximal and minimal local strain in 20 first
            smin = [ 0 ] * len(filenames)	# y direction data points.
            samax = [ 0 ] * len(filenames)	# Maximal and minimal average strain in 20 first
            samin = [ 0 ] * len(filenames)	# y direction data points.


	    # There is no average slope stuff anymore, is this so necessary?
	    # Or is this better to move this into display_average_strain.py
	    # (without printing, of course?) It could help the scaling.

            i = 0
            for fn in filenames[:30]:
                diffX, diffY, deltat, name, width, height, time = self.readData(fn)
                strainY = ( diffY[:,self.lag:] - diffY[:,:-self.lag] )/( self.lag*self.stepy )
                (x,y) = strainY.shape
		x1 = int(np.ceil(x/4))
		x2 = x-x1
		vCutSY = np.mean(strainY[x1:x2,:],0)

                smax[i]  = np.max(strainY[:,:20])
                smin[i]  = np.min(strainY[:,:20])
                samax[i] = np.max(vCutSY[:20])
                samin[i] = np.min(vCutSY[:20])

                print "smax = %g, smin = %g, samax = %g, samin = %g" % (smax[i],
                                                                        smin[i],
                                                                        samax[i],
                                                                        samin[i])
                i = i + 1

            smax = np.max(smax)
            smin = np.min(smin)
            samax = np.max(samax)
            samin = np.min(samin)

            for fn in filenames:

                print "Strain map for " + fn

                diffX, diffY, deltat, name, width, heigth, time = self.readData(fn)

	        # Getting scale, scaled height and width (in millimeters) and the ratio
		# of the height and width. Putting them inside the loop ensures that if
		# multiple samples are analyzed, each of them uses its own scale.
	        scale = self.lookForScale(name)

                # FWD difference
		# This calculates the strain numerically with forward difference (numeerinen
		# derivaatta). We can't get strain from all the sample, but 50 pixels (~1.5 mm)
		# from the bottom part of the sample goes to waste. That's why the y axis gets
		# a bit shorter than the original image was.
                strainY = ( diffY[:,self.lag:] - diffY[:,:-self.lag] )/( self.lag*self.stepy )

                (x,y) = strainY.shape
		x1 = int(np.ceil(x/4))		# Crops 1/4 away from each side
		x2 = x-x1			# in x direction.
		vCutSY = np.mean(strainY[x1:x2,:],0)	# Average strain.
                yp = np.arange(0,y)*self.stepy		# Y vector for locating each strain point, as pixels.
		xp = np.arange(0,x)*self.stepy		# X vector for locating each strain point, as pixels.
		mmDepth = [0] * len(yp)			# Y as millimeters
		mmWidth = [0] * len(xp)			# X as millimeters

		for i in range(len(yp)):
			mmDepth[i] = float(yp[i]) * scale

		for i in range(len(xp)):
			mmWidth[i] = float(xp[i]) * scale

		ratio = mmWidth[-1]/mmDepth[-1]

		# STRAIN MAP

		axissize=(0.5*(1-0.60*ratio)+0.05,0.2,0.60*ratio,0.60)

		fig=mpl.figure(num=2,figsize=(6,5),facecolor='w',edgecolor='k')
		mpl.clf() # If this is commented, every second picture turns upside-down...?
		ax=fig.add_axes(axissize)
		mpl.contourf(mmWidth, mmDepth, strainY.T * 100,50) # Into percents
                mpl.gca().invert_yaxis()
                locs, labels = mpl.yticks(fontsize=9)
                locs, labels = mpl.xticks(fontsize=9)

		mpl.axis('tight')
		mpl.xlabel("Width [mm]", fontsize=12)
		mpl.ylabel("Depth from non-fatigued side [mm]", fontsize=12)
		mpl.colorbar() # Colorbar
                savefn = fn.split('.dff')[0] + "-strainmap.pdf"
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
            
            testX		= np.zeros((dffpointsx, dffpointsy),float)
            testY		= np.zeros((dffpointsx, dffpointsy),float)
            
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
                
		xgrid		= np.arange(0,dffpointsx)
		ygrid		= np.arange(0,dffpointsy)
		refX, refY	= np.meshgrid(ygrid, xgrid)
                
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
        print "usage: display_dff_6.0.py <dff-files>"
        print "       python plotdff.py file1.dff file2.dff"
        sys.exit()

    plot = DisplayDff(sys.argv[1:])
