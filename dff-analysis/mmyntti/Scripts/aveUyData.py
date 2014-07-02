import sys
import os
import numpy as np
import matplotlib.pyplot as mpl
from scipy import stats as sp

# This script plots data from given -uy.dat files in following ways:
# 
# a) there is calculated average and median curves of both ref and fat
#    samples in their own graphs, plus curves of single samples.
# b) common graph
# c) local strain graph calculated from the average deformation curve,
#    in both ref and fat cases.
# d) all average deformation curves in the same picture, now at all moments.
#
# All curves are put in subfolder am_curves, created under the folder in which
# this script is fun in.
#
# Translations:
#
# Syvyys rasitetulta puolelta $y$ [mm]
# = Depth from fatigued side $y$ [mm]
#
# Keskisiirtyma $u_y$ [mm]
# = Average deformation $u_y$ [mm]
#
# Keskipuristuma $\epsilon_y$ [%]
# = Average strain $\epsilon_y$ [%]

class AveDiff:

	def aveDiff(self, aveMedData, xplaces):

		lag = 5 # How many data points are crossed when derivating.

		for time in aveMedData:

			averageYDataR = np.array(aveMedData[time][0])
			medianYDataR = np.array(aveMedData[time][1])
			averageYDataF = np.array(aveMedData[time][2])
			medianYDataF = np.array(aveMedData[time][3])

			aveRDiff = ( averageYDataR[lag:] - averageYDataR[:-lag] ) * 100.0 / (lag) # * 100.0 is for making it percents.
			aveFDiff = ( averageYDataF[lag:] - averageYDataF[:-lag] ) * 100.0 / (lag)
			medRDiff = ( medianYDataR[lag:] - medianYDataR[:-lag] ) * 100.0 / (lag)
			medFDiff = ( medianYDataF[lag:] - medianYDataF[:-lag] ) * 100.0 / (lag)

			# Plots
			mpl.figure(1)
			fig = mpl.figure(3)
			fig.clf()
			ax = fig.add_subplot(111)

			# Average data is drawn with solid green line and median data with dashed blue one.
			# And with fatigued, brown and purple.
			mpl.plot(xplaces[:-lag],aveRDiff,'b',label="AverageR", linewidth=3)
			#mpl.plot(xplaces[:-lag],medRDiff,'b',label="MedianR")
			mpl.plot(xplaces[:-lag],aveFDiff,'r',label="AverageF", linewidth=3)
			#mpl.plot(xplaces[:-lag],medFDiff,color='purple',label="MedianF")
		
			titlestr = ""#"strain, " + str(time)

			ax.annotate(titlestr, xy=(.5, .975), xycoords='figure fraction',
							horizontalalignment='center', 
							verticalalignment='top', fontsize=20)

			locs, labels = mpl.yticks(fontsize=15)
			locs, labels = mpl.xticks(fontsize=15)

			mpl.xlabel('Syvyys rasitetulta puolelta $y$ [mm]', {'color' : 'k', 'fontsize' : 22 })
			mpl.ylabel(r'Keskipuristuma $\epsilon_y$ [%]', {'color' : 'k', 'fontsize' : 22 })

			# And axis limits. totalYmax is not allowed to be bigger than 50, but it can be smaller.
			#totalYmax = np.max([np.max(aveRDiff), np.max(aveFDiff), np.max(medRDiff), np.max(medFDiff)])
			#totalYmin = np.min([np.min(aveRDiff), np.min(aveFDiff), np.min(medRDiff), np.min(medFDiff)])
			totalYmax = np.max([np.max(aveRDiff), np.max(aveFDiff)])
			totalYmin = np.min([np.min(aveRDiff), np.min(aveFDiff)])
			mpl.ylim(totalYmin,totalYmax)
			mpl.xlim(np.min(xplaces),np.max(xplaces))

			fname = "am_curves/am_curves-" + str(time) + "-strain.pdf"
			mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w', orientation='portrait', 
							format='pdf', transparent=False, bbox_inches=None, 
							pad_inches=0.1)

		print "Strain plotting made!"
		
	def wholePlot(self, dictionaryR, dictionaryF, xplaces):

		# This function uses yinterp-data that is saved when running 
		# drawThePlots-function and creates a picture with plots of
		# both types of sample.

		dataToReturn = {}

		for time in dictionaryR:

			ymax = 0.0
			ymin = 0.0

			# Plots
			mpl.figure(1)
			fig = mpl.figure(3)
			fig.clf()
			ax = fig.add_subplot(111)

			# Gathering interpolated y data in a list and drawing single
			# plots with a) dotted red lines (if fatigued) and b) dotted
			# cyan lines (if not).

			listOfInterpsR = []

			for name in dictionaryR[time]:
				yinterp = dictionaryR[time][name][2]
				listOfInterpsR.append(yinterp)
				mpl.plot(xplaces,yinterp,'c:',label=name+"R")
				if np.max(yinterp) > ymax:
					ymax = np.max(yinterp)
				if np.min(yinterp) < ymin:
					ymin = np.min(yinterp)

			listOfInterpsF = []

			for name in dictionaryF[time]:
				yinterp = dictionaryF[time][name][2]
				listOfInterpsF.append(yinterp)
				mpl.plot(xplaces,yinterp,'purple', linestyle="dotted", label=name+"F")
				if np.max(yinterp) > ymax:
					ymax = np.max(yinterp)
				if np.min(yinterp) < ymin:
					ymin = np.min(yinterp)

			# Making data for average line and median line.

			averageYDataR = [0] * len(xplaces)
			medianYDataR = [0] * len(xplaces)
			averageYDataF = [0] * len(xplaces)
			medianYDataF = [0] * len(xplaces)

			# Of each depth point:
			for i in range(len(xplaces)):
				# Of each sample, R:
				listOfMeaPoints = []
				for yinterp in listOfInterpsR:
					listOfMeaPoints.append(yinterp[i])
				averageYDataR[i] = np.mean(listOfMeaPoints)
				medianYDataR[i] = np.median(listOfMeaPoints)

				# Of each sample, F:
				listOfMeaPoints = []
				for yinterp in listOfInterpsF:
					listOfMeaPoints.append(yinterp[i])
				averageYDataF[i] = np.mean(listOfMeaPoints)
				medianYDataF[i] = np.median(listOfMeaPoints)

			# Average data is drawn with solid green line and median data with dashed blue one.
			# And with fatigued, brown and purple.
			mpl.plot(xplaces,averageYDataR,'b',label="AverageR", linewidth=3)
			mpl.plot(xplaces,medianYDataR,'b',label="MedianR")
			mpl.plot(xplaces,averageYDataF,'r',label="AverageF", linewidth=3)
			mpl.plot(xplaces,medianYDataF,color='r',label="MedianF")
		
			titlestr = "" #"common, " + str(time)

			ax.annotate(titlestr, xy=(.5, .975), xycoords='figure fraction',
							horizontalalignment='center', 
							verticalalignment='top', fontsize=20)

			locs, labels = mpl.yticks(fontsize=15)
			locs, labels = mpl.xticks(fontsize=15)

			mpl.xlabel('Syvyys rasitetulta puolelta $y$ [mm]', {'color' : 'k', 'fontsize' : 22 })
			mpl.ylabel(r'Keskisiirtyma $u_y$ [mm]', {'color' : 'k', 'fontsize' : 22 })

			# And axis limits. totalYmax is not allowed to be bigger than 50, but it can be smaller.
			totalYmax = np.max([np.max(averageYDataR), np.max(medianYDataR), np.max(averageYDataF), np.max(medianYDataF), ymax])
			totalYmin = np.min([np.min(averageYDataR), np.min(medianYDataR), np.min(averageYDataF), np.min(medianYDataF), ymin])
			mpl.ylim(totalYmin,totalYmax)
			mpl.xlim(np.min(xplaces),np.max(xplaces))

			fname = "am_curves/am_curves-" + str(time) + "-common.pdf"
			mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w', orientation='portrait', 
							format='pdf', transparent=False, bbox_inches=None, 
							pad_inches=0.1)

			dataToReturn[time] = [averageYDataR, medianYDataR, averageYDataF, medianYDataF]

		print "Common plotting made!"

		return dataToReturn


	def drawThePlots(self, dictionary, fatOrRef, xplaces):

		# First, making interpolated data.
		for time in dictionary:
			for name in dictionary[time]:
				x = dictionary[time][name][0]
				y = dictionary[time][name][1]
				x.reverse()
				y.reverse()
				yinterp = np.interp(xplaces, x, y)
				dictionary[time][name].append(yinterp) 

		# The own plot picture for each moment.

		for time in dictionary:

			ymax = 0.0
			ymin = 0.0

			# Plots
			mpl.figure(1)
			fig = mpl.figure(3)
			fig.clf()
			ax = fig.add_subplot(111)

			# Gathering interpolated y data in a list and drawing single
			# plots with a) dotted red lines (if fatigued) and b) dotted
			# cyan lines (if not).

			listOfInterps = []

			for name in dictionary[time]:
				yinterp = dictionary[time][name][2]
				listOfInterps.append(yinterp)
				if fatOrRef == "fat":
					mpl.plot(xplaces,yinterp,'purple',linestyle="dotted",label=name)
				else:
					mpl.plot(xplaces,yinterp,'c:',label=name)
				if np.max(yinterp) > ymax:
					ymax = np.max(yinterp)
		
				if np.min(yinterp) < ymin:
					ymin = np.min(yinterp)

			# Making data for average line and median line.

			averageYData = [0] * len(xplaces)
			medianYData = [0] * len(xplaces)

			# Of each depth point:
			for i in range(len(xplaces)):
				# Of each sample:
				listOfMeaPoints = []
				for yinterp in listOfInterps:
					listOfMeaPoints.append(yinterp[i])
				averageYData[i] = np.mean(listOfMeaPoints)
				medianYData[i] = np.median(listOfMeaPoints)

			# Average data is drawn with solid green line and median data with dashed blue one.
			# Or, in fatigued case, brown and purple one.
			if fatOrRef == "fat":
				mpl.plot(xplaces,averageYData,'r',label="Average", linewidth=3)
				mpl.plot(xplaces,medianYData,color='r',label="Median")
			else:
				mpl.plot(xplaces,averageYData,'b',label="Average", linewidth=3)
				mpl.plot(xplaces,medianYData,'b',label="Median")
		
			titlestr = ""#fatOrRef + ", " + str(time)

			ax.annotate(titlestr, xy=(.5, .975), xycoords='figure fraction',
							horizontalalignment='center', 
							verticalalignment='top', fontsize=20)

			locs, labels = mpl.yticks(fontsize=15)
			locs, labels = mpl.xticks(fontsize=15)

			mpl.xlabel('Syvyys rasitetulta puolelta $y$ [mm]', {'color' : 'k', 'fontsize' : 22 })
			mpl.ylabel(r'Keskisiirtyma $u_y$ [mm]', {'color' : 'k', 'fontsize' : 22 })

			# And axis limits. totalYmax can't be bigger than 50.
			totalYmax = np.max([np.max(averageYData), np.max(medianYData), ymax])
			totalYmin = np.min([np.min(averageYData), np.min(medianYData), ymin])
			mpl.ylim(totalYmin,totalYmax)
			mpl.xlim(np.min(xplaces),np.max(xplaces))
		
			# Save the single-plots
			if not os.path.exists("am_curves"):
				os.makedirs("am_curves")

			fname = "am_curves/am_curves-" + str(time) + "-" + fatOrRef + ".pdf"
			mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w', orientation='portrait', 
							format='pdf', transparent=False, bbox_inches=None, 
							pad_inches=0.1)

		print "Single plotting made for " + fatOrRef + " case!"
		

	def __init__( self, filenames ):

		# Making x vector

		accur = 50.0 # In how many parts one mm is divided. Is a float.
		height = 8 # Wished usable height, in mms.

		initialXplaces = range(int(accur)*height)
		thenXplaces = [0] * (int(accur)*height)

		for i in range(int(accur)*height):
			thenXplaces[i] = float (initialXplaces[i] / accur)

		self.xplaces = thenXplaces

		# At first, the -uy.dat files are sorted by their time and name.
		# We assume that we have moments 50, 100, 150, ... , 450. So, we
		# have a two-level dictionary:
		# Uppest dictionary: 
		#	keys = times
		#	contents = subdictionary
		# Subdictionary: 
		#	keys = sample names
		#	contents = two-place list with x and y data.

		dictionaryR = {}	# Dictionary for reference samples
		dictionaryF = {}	# Dictionary for fatigued samples

		for fn in filenames:

			#print "Average uy data gathering for " + fn

			# Data gathering

			splitFnLine = fn.split("-")
			time = int(splitFnLine[-2])
			splitFnIB = fn.split("IB")
			name = "IB" + splitFnIB[-1]
			#splitter = name + "-dff-"
			#path = fn.split(splitter)[0]

			# Gathering xy data

			file = open(fn,'r')
			data = file.readlines()
			file.close()

			length = len(data)
			x = [0] * length
			y = [0] * length

			for i in range(length):
				splitData = data[i].split(", ")
				x[i] = float(splitData[0])
				y[i] = float(splitData[1].split("\n")[0])

			# Putting data into right place:
			# Check if there is already a key for that time. If not,
			# it is made.

			fatOrRef = name[6].capitalize()

			if fatOrRef == "R":

				if not dictionaryR.has_key(time):
					dictionaryR[time] = {}

				# Adding subdictionary about the name, x and y data and fatigueness of the sample.
				dictionaryR[time][name] = [x,y]

			else:

				if not dictionaryF.has_key(time):
					dictionaryF[time] = {}

				# Adding subdictionary about the name, x and y data and fatigueness of the sample.
				dictionaryF[time][name] = [x,y]

		# After sorting the data into dictionaries, we can start to make average
		# and median curves of them.

		print "Data gathering made!"

		self.drawThePlots(dictionaryR, 'ref', self.xplaces)
		self.drawThePlots(dictionaryF, 'fat', self.xplaces)
		aveMedData = self.wholePlot(dictionaryR, dictionaryF, self.xplaces)
		# aveMedData means: dictionary[time] = [averageYDataR, medianYDataR, averageYDataF, medianYDataF]
		self.aveDiff(aveMedData, np.array(self.xplaces))

		aveYDataR = {}
		aveYDataF = {}
		timelist = []

		for time in aveMedData:
			aveYDataR[time] = aveMedData[time][0]
			aveYDataF[time] = aveMedData[time][2]
			timelist.append(time)

		timelist.sort()

		ymax = 0.0
		ymin = 0.0
		index = 0

		# Plots
		mpl.figure(1)
		fig = mpl.figure(3)
		fig.clf()
		ax = fig.add_subplot(111)

		for time in timelist:
			# ls stuff is for changing line styles, thickness for line thickness.
			ls = 'solid'
			thickness = (index/4)*2 + 1
			if index%4 == 0:
				ls = ':'
			if index%4 == 1:
				ls = '-.'
			if index%4 == 2:
				ls = '--'
			mpl.plot(self.xplaces,aveYDataR[time],'b',label=str(time)+"r", linestyle=ls, linewidth=thickness)
			mpl.plot(self.xplaces,aveYDataF[time],'r',label=str(time)+"r", linestyle=ls, linewidth=thickness)
			index = index + 1
		
		titlestr = ""#"Average Strains"
		ax.annotate(titlestr, xy=(.5, .975), xycoords='figure fraction',
						horizontalalignment='center', 
						verticalalignment='top', fontsize=20)

		locs, labels = mpl.yticks(fontsize=15)
		locs, labels = mpl.xticks(fontsize=15)
		mpl.xlabel('Syvyys rasitetulta puolelta $y$ [mm]', {'color' : 'k', 'fontsize' : 22 })
		mpl.ylabel(r'Keskipuristuma $\epsilon_y$ [%]', {'color' : 'k', 'fontsize' : 22 })
		#mpl.ylim(-0.2,4.0)
		fname = "am_curves/averageStrains.pdf"
		mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w', orientation='portrait', 
						format='pdf', transparent=False, bbox_inches=None, pad_inches=0.1)

		print "Common average strain plotting made!"

if __name__=="__main__":
    usage = "Usage :\t python AveuyData.py filenames (they are -uy.dat files)"
	
    if len(sys.argv) < 1:
        print usage
        sys.exit()
        
    filenames = sys.argv[1:]
    runAnalysis = AveDiff(filenames)
