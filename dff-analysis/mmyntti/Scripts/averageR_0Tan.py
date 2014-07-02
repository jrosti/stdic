# Average r_0 calculated from several annual ring pieces. This script is for case in which theta -> 0, in other words here is visible several short pieces of annual rings.
#
# In this script, A means the left-most annual ring and B right-most annual ring (though there is actually no matter with their order). Aa means the start point of the visible part of the A ring (the more clockwise one) and Ab the end point (same thing with Ba and Bb). Aax means the x coordinate of the start point of the A ring, and so on. d is the distance between the rings (not accuratelly, measured from midpoints of lines Aa-Ab and Ba-Bb).

import numpy as np
from sys import *
from math import *

# Calculating theta, meaning the angle coordinate of the chosen annual ring.

def calculateThetaRad(ax,ay,bx,by):
	thetaIsMoreThanPi = False
	if (ax < bx):
		thetaIsMoreThanPi = True
	smallNumber = 0.000001
	if (abs(by-ay)<smallNumber):
		return pi/2
	thetaR = atan((bx-ax)/(by-ay))
	if (thetaR < 0):
		thetaR = thetaR + pi
	if thetaIsMoreThanPi:
		thetaR = thetaR + pi
	return thetaR

# Calculated the distance between annual rings, d. It makes lines between the start and end points of the annual rings, calculated their midpoints and measures their distance.
def calculateD(Aax, Aay, Abx, Aby, Bax, Bay, Bbx, Bby):
	Cax = (Aax+Abx)/2.0
	Cay = (Aay+Aby)/2.0
	Cbx = (Bax+Bbx)/2.0
	Cby = (Bay+Bby)/2.0
	d = sqrt(abs(Cax-Cbx)**2+abs(Cay-Cby)**2)
	return d

# Calculating r_0. Values are given in pixels, result is given in millimeters.
def radiusZero(Aax, Aay, Abx, Aby, Bax, Bay, Bbx, Bby, trans):
	alfa = calculateThetaRad(Aax, Aay, Abx, Aby)
	beta = calculateThetaRad(Bax, Bay, Bbx, Bby)
	d = calculateD(Aax, Aay, Abx, Aby, Bax, Bay, Bbx, Bby)
	smallNumber = 0.000001
	if abs((1/tan(alfa)) - (1/tan(beta))) < smallNumber:
		return 0 # In other words: Failed, angles alfa and beta are equal, the radius should be infinite.
	r = d / abs(1/tan(alfa) - (1/tan(beta)))
	pixmm = r*trans # Transformation to millimeters.
	return pixmm

# Lists of points in annual rings. There is chosen the clearest annual rings. The lists contain four-place lists that contain [Aax, Aay, Abx, Aby] or [Bax, Bay, Bbx, Bby], depending on the list. The inactive lists are commented.

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~

# Board IB7-15

name = "IB7-15"
trans = 96.0/2075.0 # Transformation to millimeters. 96.0 is the width of the board in millimeters, the other number is the width of the board visible in the picture.
ARingList =    [[800.0,1045.0,605.0,800.0],
		[545.0,1040.0,300.0,800,0],
		[845.0,1045.0,665.0,805.0]]
BRingList =    [[2170.0,1035.0,2095.0,800.0],
		[1980.0,1040.0,1885.0,800.0],
		[2105.0,1040.0,2025.0,805.0]]

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~

amountA = len(ARingList)
amountB = len(BRingList)
amountR = amountA*amountB

results = [0]

print "\nBoard: %s \n" % (name)
print "There was calculated \n%d different values for r_0 with \n%d left-most rings and \n%d right-most rings." % (amountR, amountA, amountB)

for a in ARingList:
	for b in BRingList:
		r_0 = radiusZero(a[0],a[1],a[2],a[3],b[0],b[1],b[2],b[3],trans)
		print r_0
		if (a == 0):
			if (b == 0):
				results[0] = r_0
		else:
			results.append(r_0)

# Now there is different r_0:s in list results. Let's calculate the average value.

rsum = 0.0
for r in results:
	rsum = rsum + r
average = rsum/amountR
print "The average value for r_0 is %6.6f mm." % (average)

# Standard deviation (otoskeskihajonta)

sumsd = 0.0
for r in results:
	sumsd = sumsd + (r - average)**2
sd = sqrt(sumsd/(amountR - 1))
print "The standard deviation for r_0 is %6.6f mm." % (sd)

# Standard error (keskivirhe)

error = sd/sqrt(amountR)
print "The standard error for r_0 is %6.6f mm.\n" % (error)
