#!/usr/bin/env python


import matplotlib.pyplot as plt
from numpy import *
import sys

####Read file and calculate the vertical displacement 
def readydata(filename):
    file = open(filename, 'r')
    ydata =[]
    matData = []
    xcoord = 0
    prevxcoord = 0
    cols = 1
    TIME = float()
    DELTAT = float()
    TimeTest = 0.0

    while 1:
        line = file.readline()
        if not line:
            break
        data = line.split()
        if line[0] == '%':
            if data[1] == 'time:': 
                TIME = float(data[2])
            elif data[1] == 'delta:':
                DELTAT = float(data[2])
            continue

        xcoord = int(data[0])
        if xcoord > prevxcoord:
            cols = cols + 1
        ycoord = int(data[1])
        ydata.append((float(data[3]))-float(data[1]))
        prevxcoord = xcoord
    Z = array(ydata)
    rows = Z.shape[0]/cols
    TimeTest = TIME # Time -  write here the time of the first dff file
    matData = transpose(Z.reshape(cols, rows))
    return (TimeTest, matData[1:(matData.shape[0]-1), 1:(matData.shape[1]-1)])
    
    
###Calculate the strain as difference of displacements on length 40 (> crate 32)   
def relstrain(Zh): 
	mat = zeros(Zh.shape)
	for j in range (5, Zh.shape[0]):
		for i in range (0, Zh.shape[1]):
			mat[j,i] = (Zh[j,i]-Zh[j-4, i])/40.0
	return mat[5:(Zh.shape[0]-1), 1:(Zh.shape[1]-1)]


###Compute average value and fluctuations of the considered field
def computefluc(A): #Zh):
    #A = relstrain(Zh)
    N = product(shape(A))
    m1 = sum(A)/N
    m2 = sum(A*A)/N
    m3 = sum(A*A*A)/N
    m4 = sum(A*A*A*A)/N
    variance = m2 - m1*m1
    stddev = sqrt(variance)
    thirdcentralmoment = (m3 - 3 * m1* m2 + 2*m1**3)
    skewness = thirdcentralmoment/stddev**3
    return (m1, variance, skewness, stddev, thirdcentralmoment)

###Main
sys.argv.pop(0)
file = sys.argv.pop(0)
(time, z)  = readydata(file)
strainmat = relstrain(z)
(averaged, var, skewn, fluc, moment3) = computefluc(strainmat)
print time, averaged, var, skewn, fluc, moment3



