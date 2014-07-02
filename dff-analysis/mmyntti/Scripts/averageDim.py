import numpy
import os
from glob import glob
from scipy import stats as sp
from sys import *
from math import *

# This script can be used for calculating average dimensions for
# samples and taking scales for "transforming fatigue samples to
# non-fatigued one and taking theta_mm angle" (used in
# plotTTMData-2.0.py script, see there). Latest one with z
# dimensions (DIM = 4). Prints only to terminal.

# Reading dimension values from dict.csv.

DIM = 4 # 2 = x dimension, 3 = y dimension, 4 = z dimension

data = numpy.loadtxt("/media/matleena_csm_usb/Dataa/Common/dict.csv",dtype="string",comments='#',delimiter=',')
fnData = {}
dataLen = data.shape[0]
sumF = 0.0
sumR = 0.0
lenF = 0
lenR = 0
stanDF = 0
stanDF = 0

for i in range(dataLen):
	letter = data[i, 0][19]
	if letter == "F":
		sumF = sumF + float(data[i, DIM].strip()) 
		lenF = lenF + 1
	else:
		sumR = sumR + float(data[i, DIM].strip()) # 2 = x dimension, 3 = y dimension, 4 = z dimension
		lenR = lenR + 1

averageF = sumF / lenF
averageR = sumR / lenR
scale = averageR / averageF
scale2 = 1.0/scale

sumsdF = 0.0
sumsdR = 0.0
amountF = 0
amountR = 0

for i in range(dataLen):
	letter = data[i, 0][19]
	if letter == "F":
		sumsdF = sumsdF + (float(data[i, DIM].strip()) - averageF)**2
		amountF = amountF + 1
	else:
		sumsdR = sumsdR + (float(data[i, DIM].strip()) - averageR)**2
		amountR = amountR + 1

sdF = sqrt(sumsdF/(amountF - 1))
sdR = sqrt(sumsdR/(amountR - 1))

errorF = sdF/sqrt(amountF)
errorR = sdR/sqrt(amountR)

print ""
print "REFERENCE"
print "Average: %f mm." % averageR
print "St.dev.: %f mm." % sdR
print "Error  : %f mm." % errorR
print ""
print "FATIGUED"
print "Average: %f mm." % averageF
print "St.dev.: %f mm." % sdF
print "Error  : %f mm." % errorF
print ""
print "Thus, the scale is %f." % scale
print "And, in the other direction, %f." % scale2
print ""
