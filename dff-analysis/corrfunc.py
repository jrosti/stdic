#!/usr/bin/env python

import sys
import dff

def correlation(Zh, l):
	count = 0.0
	sum = 0.0
	for i in range(0, Zh.shape[1]-l-1): 
		for j in range(0, Zh.shape[0]-1):
			sum = sum + (Zh[j,i]-Zh[j,i+l])**2
			count = count + 1
#	print sum, count
	sum = sum / count
	return sum

sys.argv.pop(0)
name = sys.argv.pop(0)
for l in range(1, 5,1):
	fd = open(name + "." + str(l) + ".dat", 'w')
	for i in range(0, len(sys.argv)):
		deformation = dff.dff(sys.argv[i])
		relativestrains = deformation.get_relativestrain()
		fd.write("%lf %e\n" %  (deformation.get_time(), correlation(relativestrains, l)));
	fd.close()
