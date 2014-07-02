import sys
import os
import numpy as np
import matplotlib.pyplot as mpl
from scipy import stats as sp

# This function calculates average deformations u_y(y) and puts them into
# .dat file and a graph.

NUM_LIN_FITS = 1 	# The rest of the script is designed mainly for one slope case, be
			# careful! It doesn't moan if there is more slopes, but it doesn't
			# gather data about extra slopes, either.

class AveDiff:
	"""
	BEFORE USING THIS SCRIPT, RUN xAnalysis.py WITH YOUR SAMPLES TO GET SCALES!
	"""
	def polylin(self, data, N):
	    """
	    Fit N straights to evenly divided parts of data.  The data should be
	    of the form [ X, Y ] where X and Y are sub vectors (meaning:
	    data = [ [x0, x1, x2...], [y0, y1, y2...]).
	    Taken and modified from plotTTMData.py script. Since there is far less data
	    points than in Instron data, the data points on the limits will be shared.
	    """
	    coeff  = [np.array([])] * N # Here is stored "a" and "b" of "y = ax + b"
	    bounds = [np.array([])] * N # Here is stored the start and the end point of each slope
	    parts  = [np.array([])] * N # Here is stored th data to be plotted in each section.

	    blocklen = int( np.ceil( float( len(data) )/N ) ) 	# blocklen tells how many data points
								# are used in each section. np.ceil(x)
								# rounds x to an integer that is equal
								# or larger than x. 
	
	    # Divides data into sections and puts them to "parts" list.
	    for i in np.arange(0,N):
		f = i * blocklen		# from (as indexes)
		t = ( i + 1 ) * blocklen	# to (as indexes)
		if i < N-1:
		        parts[i] = data[f:t][:]
		else:
		        parts[i] = data[f:][:]

	    # Gets slope data for each data section in "parts" list.
	    for i in np.arange(0,N):
		block = parts[i]
		x = [0] * len(block)
		y = [0] * len(block)
		for k in range(len(block)):
			x[k] = float(block[k][0])
			y[k] = float(block[k][1])
		p, residuals, rank, singular_values, rcond = np.polyfit(x,y,1,full=True)
		bounds[i] = [ x[0], x[-1] ]
		coeff[i] = [ p[0], p[1] ]

	    #return bounds, coeff, r_value, p_value, std_err
	    return bounds, coeff, residuals[0]



	def lookForScale(self, dataFile, name):
	    """
	    Looks for the scale of the given name from given data file.
	    """
	    width = open(dataFile,'r')
	    widthData = width.readlines()
	    width.close()

	    scale = 1.0 	# If the real scale can't be found, the script 
	    			# doesn't scale at all but keeps the original
				# pixel measurements. You'll notice if it happens.

	    # Looking for the scale of given name.
	    for i in range(len(widthData)):
		widthSplitData = widthData[i-1].split(", ")
		if name in widthSplitData:
		    scale = float(widthSplitData[1].strip())
		else:
		    continue

	    return scale


	def saveAndSort(self, filename, name, coeff, residual, end):
        	"""
        	Saves data into textfiles filename-aveStrainSlopes.end (end is with dot,
		like ".txt"). Also three subfiles consisting of only time and some other
		variable, like constant (for making xmgrace plotting easier). Also sorts
		already existing data. Shell script takes care of replacing old data files 
		with new ones.
        	"""

		timeCurrent = int(filename.strip(".dff").split("-")[-1])
		dataFileName = filename.split("crop_")[0] + name + "-aveStrainSlopes" + end
		dataFileNameSlope = filename.split("crop_")[0] + name + "-slope-aveStrainSlopes" + end
		dataFileNameConstant = filename.split("crop_")[0] + name + "-constant-aveStrainSlopes" + end
		dataFileNameResidual = filename.split("crop_")[0] + name + "-residual-aveStrainSlopes" + end
			

		# Adding data to main file
		file = open(dataFileName, 'a') # File opened for appending: nothing is removed.
		sf = "%d %e %e %e \n" % (timeCurrent/10, coeff[0][0], coeff[0][1], residual) 
		file.write(sf)
		file.close()

		# Sorting already existing data
		file = open(dataFileName, 'r') # File opened for reading.
		lines = file.readlines()
		file.close()
		lineData = {}
		for i in range(len(lines)):
			lines[i] = lines[i].split(" ")
			time = int(lines[i][0])
			slope = float(lines[i][1])
			constant = float(lines[i][2])
			residual = float(lines[i][3])
			contents = [slope, constant, residual]
			lineData[time] = contents
		lineList = lineData.keys()
		lineList.sort()

		fileMain = open(dataFileName, 'w') # File opened for writing: old data is erased
		fileSlope = open(dataFileNameSlope, 'w')
		fileConstant = open(dataFileNameConstant, 'w')
		fileResidual = open(dataFileNameResidual, 'w')

		for t in lineList:
			mainData = "%d %e %e %e \n" % (t, lineData[t][0], lineData[t][1], lineData[t][2])
			fileMain.write(mainData)
			slopeData = "%d %e \n" % (t, lineData[t][0])
			constantData = "%d %e \n" % (t, lineData[t][1])
			residualData = "%d %e \n" % (t, lineData[t][2])
			fileSlope.write(slopeData)
			fileConstant.write(constantData)
			fileResidual.write(residualData)
		fileMain.close()
		fileSlope.close()
		fileConstant.close()
		fileResidual.close()

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




	def __init__( self, filenames ):

        	self.lag = 1		# A constant used in numeric derivating.
                self.stepy = None	# Distance between the data points in DIC:ing
					# (read in dff in readData, usually 10 pixels)
		for fn in filenames:

			print "Average diffY curve for " + fn

		        diffX, diffY, deltat, name, width, height, time = self.readData(fn)
	     		scale = self.lookForScale("/home/mmyntti/Scripteja/xResults.csv", name)

		        (x,y) = diffY.shape
			x1 = int(np.ceil(x/4)) 		# Crops 1/4 away from each side
			x2 = x-x1			# in x direction.
			avDiff = np.mean(diffY[x1:x2,:],0)	# Average movement
		        yp = np.arange(0,y)*self.stepy		# Vector for locating each strain point, as pixels. 
			mmDepth = [0] * len(yp)			# Same as millimeters
			mmAvDiff = [0] * len(yp)

			for i in range(len(yp)):
				mmDepth[i] = float(yp[i]) * scale
				mmAvDiff[i] = float(avDiff[i]) * scale

			movementData = zip(mmDepth, mmAvDiff)
			x = mmDepth # Too lazy to change, I just place it on x.
			x.reverse() # Also reversing the order for making it to count from the fatigued side
				    # instead from non-fatigued one
			y = mmAvDiff  # -||- without reversing.

			# Saving average straing data as millimeters and percents
			out = np.array(zip(mmDepth, mmAvDiff), dtype=[('Depth', float),('float', float)])
			outFile = fn.split(".dff")[0] + "-uy.dat"
			np.savetxt(outFile, out, fmt="%f, %f")

			# Cropping bad data points away. (For fitting the line.)

			startIndex = 0
			startOK = 0 	# The start point is taken just once.
			endIndex = 0

			# Taking three first and three last data points away. We assume that
			# there is more than 7 data points.

			startIndex = 3
			endIndex = len(movementData) - 3

			# Making fixed x and y vectors:
			distance = endIndex - startIndex # Start and end points are taken, too.
			xf = [0] * distance
			yf = [0] * distance
			for i in range(startIndex, endIndex):
				xf[i-startIndex] = x[i]
				yf[i-startIndex] = y[i]
			fixedData = zip(xf, yf)

			#bounds, coeff, r_value, p_value, std_err = self.polylin(fixedData, NUM_LIN_FITS)
			bounds, coeff, residual = self.polylin(fixedData, NUM_LIN_FITS)	

			# Saving data to text file to aveStrainSlopes.txt which can be found from the 
			# parent folder of the folder of dff data.
			# THIS SAVES THE FIRST SLOPE DATA ONLY! Add slots if you want more slope data.

			self.saveAndSort(fn, name, coeff, residual, ".txt")
			self.saveAndSort(fn, name, coeff, residual, ".csv")

			# Plots
			mpl.figure(1)
			fig = mpl.figure(3)
			fig.clf()
			ax = fig.add_subplot(111)

			mpl.plot(x,y,label="Curve")

			for i in np.arange( 0, len(coeff) ):
				xs = np.array(bounds[i]) 			# Taking the start and the end points of i:s area.
				ys = xs.copy() * coeff[i][0] + coeff[i][1] 	# y = a*x + b
				mpl.plot( xs, ys, 'k-', linewidth=2) 		# Plotting it onto the picture.
			for i in np.arange( 0, len(coeff) ):
				xs = np.array(bounds[i])
				mpl.plot([xs[0],xs[0]],[min(y),max(y)], 'k:')	# Putting vertical dashed lines between the areas.
			mpl.plot([xs[1],xs[1]],[min(y),max(y)], 'k:')		# Putting the last dashed line.
		
			titlestr = name

			ax.annotate(titlestr, xy=(.5, .975), xycoords='figure fraction',
							horizontalalignment='center', 
							verticalalignment='top', fontsize=20)

			locs, labels = mpl.yticks(fontsize=9)
			locs, labels = mpl.xticks(fontsize=9)

			mpl.xlabel('Depth from fatigued side $y$ [mm]', {'color' : 'k', 'fontsize' : 15 })
			mpl.ylabel(r'Avg. u_y [mm]', {'color' : 'k', 'fontsize' : 15 })

			# And axis limits
			mpl.ylim(np.min(y),np.max(y))
			mpl.xlim(np.min(x),np.max(x))
		
			# Save the single-plots
			fname = fn.split('.dff')[0] + "-uy.pdf"
			#fname = fn.split('dff-')[0] + name + "-" + str(timeCurrent) + "-avgstrain.pdf"
			mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w', orientation='portrait', 
							format='pdf', transparent=False, bbox_inches=None, 
							pad_inches=0.1)


if __name__=="__main__":
    usage = "Usage :\t python uyData.py filenames"
	
    if len(sys.argv) < 1:
        print usage
        sys.exit()
        
    filenames = sys.argv[1:]
    runAnalysis = AveDiff(filenames)
