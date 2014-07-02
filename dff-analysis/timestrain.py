#!/usr/bin/env python

import sys
import dff
import numpy

def computeStrainRate(dffs):
	time = []
	relstrain = []
	for dff in dffs:
		relstrain.append(dff.get_averagestrain())
		time.append(dff.get_time())	
	f  = numpy.polyfit(time, relstrain,1)
	return f[0]

sys.argv.pop(0)
deformations = []
for i in range(0, len(sys.argv)):
	deformations.append(dff.dff(sys.argv[i]))

running = []
running.append(deformations.pop(0))
running.append(deformations.pop(0))
running.append(deformations.pop(0))
running.append(deformations.pop(0))
running.append(deformations.pop(0))

while deformations:
	print running[2].get_time(), computeStrainRate(running), running[2].get_averagestrain()
	running.append(deformations.pop(0))
	running.pop(0)