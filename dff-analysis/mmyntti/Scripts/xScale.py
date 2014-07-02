import numpy
import os
from glob import glob
from scipy import stats as sp
from sys import *
from math import *

# This script calculates the error with measuring the width of the sample (x)
# and, most importantly, creates scales for 

# Reading pixel values from xDim.tex and "real" (flawed) mm values from dict.csv.

pixelData = numpy.loadtxt("xDim.tex",dtype="string",comments='#',delimiter=',')
mmData = numpy.loadtxt("/media/matleena_csm_usb/Lumikki-dataa_IB7-1/dict.csv",dtype="string",comments='#',delimiter=',')
fnData = {}

for i in range(pixelData.shape[0]):

	# Taking just the name of the image, not the whole path. (For getting mm data, too.)
	fnRaw=pixelData[i, 0].strip()
	fnPieces=fnRaw.split("/")
	fnLen=len(fnPieces)
	fn=fnPieces[fnLen-1]

	# Other calculations:
	x1=float(pixelData[i, 1].strip())
	x2=float(pixelData[i,2].strip()) 
	x3=float(pixelData[i,3].strip()) 
	angle_r=float(pixelData[i,4].strip()) 
	angle_l=float(pixelData[i,5].strip()) 
	x0r=float(pixelData[i,6].strip()) 
	x0l=float(pixelData[i,7].strip()) 
	
	# Reading measured widths as mm's to get scales. First we have to find the corresponding measument.
	mmValue = 0

	for j in range(mmData.shape[0]):
		if fn in mmData[j,0].strip(): #If the filename contains the image name
			mmValue = float(mmData[j,2].strip())
		else:
			continue
			

	dictionaryData=[x1,x2,x3,angle_r,angle_l,x0r,x0l,mmValue] 
	fnData[fn]=dictionaryData

# This is the list of files to process
fnList = fnData.keys()
fnList.sort()

# In this case, it's okay to overwrite results.
saveToFile = True
file = open("xResults.csv", 'w')
firstline="#fileName, scale, trueWidth, measWidth, difference, xAverage, x0Average, error, errorPer, stuff\n"
file.write(firstline)


for fn in fnList:

	x1=fnData[fn][0]
	x2=fnData[fn][1] 
	x3=fnData[fn][2]
	x0r=fnData[fn][5]
	x0l=fnData[fn][6]
	mmValue = fnData[fn][7]

	xAve = (x1 + x2 + x3)/3.0
	x0Ave = (x0r + x0l)/2.0
	error = abs(xAve-x0Ave)/xAve
	errorPer = error * 100
	scale = 1
	smallNumber = 0.0000001

	if (abs(mmValue) > smallNumber):
		scale = mmValue/x0Ave
	else:
		# Means that the asked sample isn't in dict.csv
		del fnData[fn]
		continue

	trueWidth = xAve * scale

	# Save data
	if saveToFile==True:
		sf = "%s, %e, %e, %e, %e, %e, %e, %e, %e, %s\n" % (fn, scale, trueWidth, mmValue, abs(mmValue - trueWidth), xAve, x0Ave, error, errorPer, "")
		file.write(sf)

if saveToFile==True:
	file.close()
else:
	print "'xResults.csv' already exists! Data not saved!"
