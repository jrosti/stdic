# Average r_0 calculated from several points on the chosen annual ring. This script is for case in which theta -> 90, in other words here is few long pieces of annual rings and thus three point method can be used.

import numpy as np
from sys import *
from math import *

# Slope of two given points
def slope(ax, ay, bx, by):
	s = (by-ay)/(bx-ax)
	return s

# Angle ABC as radians. Because the visible piece of an annual ring can be presumd to be less than a pi, we can say that angle ABC > pi/2. That's why a is taken from pi to get the angle. 
def angle(ax, ay, bx, by, cx, cy):
	s1 = slope(ax, ay, bx, by)
	s2 = slope(bx, by, cx, cy)
	a = atan(abs ((s1 - s2)/(1 + s1*s2)))
	rad = pi - a 
	return rad

# Distance between points
def distance(ax, ay, bx, by):
	d = sqrt((bx-ax)**2 + (by-ay)**2)
	return d

# Calculating r
def radius(ax, ay, bx, by, cx, cy, trans):
	d = distance(ax, ay, cx, cy)
	a = angle(ax, ay, bx, by, cx, cy)
	b = pi - a
	r = abs(d)/(2*sin(b)) # The three point method.
	toMms = r*95.0/1277.2
	return toMms

# List of points along the board. The points are given as two-place list containing x and y coordinates of the point. 
# Remember to put the points IN ORDER (according to x coordinate)!
# And comment away the data you are not using!
# Also, put AT LEAST three (3) points to pointList!
#
#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~
#
# The first used nameless board

#name = "Eka lauta"
#pointList = [[486.0,1130.0],[590.0,1080.0],[708.0,1044.0],[818.0,1025.0],[927.0,1020.0],[1018.0,1023.0],[1205.0,1065.0],[1388.0,1130.0]]
#trans = 95.0/1277.2

#name = "IB151-4" #fat
#pointList = [[704,1158],[877,1087],[984,1055],[1080,1033],[1141,1023],[1130,1020],[1215,1014],[1271,1004],[1357,993],[1475,987],[1585,994],[1687,1010],[1794,1044],[1875,1061]]
#trans = 95.0/1869.9

name = "IB151-3" #ref
pointList = [[645,717],[841,637],[997,596],[1113,575],[1250,564],[1362,559],[1443,563],[1530,568],[1647,581],[1727,591],[1803,607],[1904,631],[2011,669]]
trans = 95.0/2228.8

#~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.~

listLen = len(pointList)
print "Board: %s \nThere was used %d points in this calculation." % (name, listLen)

# Picking groups of three points and calculating r_0 according to them. There is chosen 3 different groups; for example, if we have points 1, 2, 3, 4, the groups are 1,2,3 and 1,2,4 and 1,3,4 and 2,3,4. From these groups, r_0 is calculated, and r_0 is stored to list results.

results = [0]
i = listLen - 1
switcher = 0 # Is changed to 1 when there is added an r_0 first time.

while i >= 2:
	c = pointList[i]
	j = i - 1
	while j >= 1:
		b = pointList[j]
		k = j - 1
		while k >= 0:
			if (abs(i-j) > 2 and abs(j-k) > 2): # We don't want to use points that are too close to each others, they give funny results.
				a = pointList[k]
				r_0 = radius(float(a[0]), float(a[1]), float(b[0]), float(b[1]), float(c[0]), float(c[1]), trans)
				# Adding r_0 to results, switcher tells if the first r_0 is put already.
				print r_0
				if (switcher == 0):
					results[0] = r_0
					switcher = 1
				else:
					results.append(r_0)
			k = k - 1
		j = j-1
	i = i -1

amountR = len(results)		
print "The points gave %d results." % (amountR)

# Now there is different r_0:s in list results. Let's calculate the average value.

rsum = 0.0
for r in results:
	rsum = rsum + r
average = rsum/amountR
print "The average value is %6.6f mm." % (average)

# Standard deviation (otoskeskihajonta)

sumsd = 0.0
for r in results:
	sumsd = sumsd + (r - average)**2
sd = sqrt(sumsd/(amountR - 1))
print "The standard deviation for r_0 is %6.6f mm." % (sd)

# Standard error (keskivirhe)

error = sd/sqrt(amountR)
print "The standard error is %6.6f mm.\n" % (error)
