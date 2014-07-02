import numpy
import os
from glob import glob
import matplotlib.pyplot as mpl
from scipy import stats as sp
from sys import *
from math import *

# This script assumes that the raw TTM data is stored at the current
# working directory (CWD) when it it executed. The raw data should
# be named in the following way:
#
# "201106071140_IB7-1-R25-201106071136"
#
# where "201106071140" and "201106071136" are time stamps saved by
# labview; "IB7-1-R25" is the sample name, in which "IB7-1" is sample
# set name (5 characters), "R" tells if the sample is reference sample
# or fatigued sample ("F" is for fatigued), and "25" is the sample
# number of the sample set in question. The correct format of the file
# name is important: otherwise the program makes wrong tags.
#
# In addition to the data files, we also need the file dict.csv located
# in the same folder than the data files and this script. More
# information in that file.
#
# This script writes:
#
# a) yield points and other similar data to yield.csv
# b) interpolated stress-strain data to dataFilename-interp.csv
# c) interpolated stress-strain data with scaling to MPas to
#    dataFilename-interpScale.csv (for nicer plotting)
# d) coefficents of linear fits to dataFileName-slopes.csv
# e) plots of the linear fits are saved in the subdirectory plots.
#
# Please note that in a) none of the values are translated by eps0
# and that all of the interpolated data b) is translated left by eps0!

### CONSTANTS ################################################
RAWPPS        = 500.0                # pps in the raw data   #
PPS           = 10.0                 # pps to interpolate to #
LAG           = 3.0*PPS              # 5 s lag ~= 1.7% strain#
SED           = 0.5                  # skip % of mdiff       #
NUM_LIN_FITS  = 4                    # # of fits for slopes  #
SCALE	      = 1.039188	     # scale for fatigued    #
##############################################################

# RAWPPS is the sample rat in the raw data files
# PPS is the sample rate to which the data is interpolated.
# LAG is the lag used in the numerical derivatives
# SED is the ammount of strain to skip when looking for steepest part
#     of the stress strain curve (young's modulus)
# NUM_LIN_FITS is the ammount of straights to try to fit into the
#              stress strain curves in order to obtain the plateu
#              slope. The number 4 seems to work pretty well.
# SCALE is a value [average height of reference samples] divided by
#		[average height of fatigued samples], calculated
#		separately. This is used for creating estimate of
#		the theta angles of the fatigues samples when they
#		weren't fatigued yet.
#
# In case of you are non-Finnish-speaking user, some translations
# (I needed Finnish labels):
#	rasitus   = stress
# 	puristuma = strain

def monotonize(list):
	"""
	Make list non-decreasing (not really monotonic strictly speaking).
	"""
	for i in range(0,len(list)-1):
		if list[i] > list[i+1]:
			list[i+1] = list[i]

def polylin(data,N):
	"""
	Fit N straights to evenly divided parts of data.  The data should be
	of the form [ X, Y ] where X and Y are column vectors.
	"""
	coeff  = [numpy.array([])] * N # Here is stored "a" and "b" of "y = ax + b"
	bounds = [numpy.array([])] * N # Here is stored the start and the end point of each slope
	parts  = [numpy.array([])] * N # Here is stored th data to be plotted in each section.
	blocklen = int( numpy.ceil( len(data) / N ) )

	for i in numpy.arange(0,N):
		f = i * blocklen             # from
		t = ( i + 1 ) * blocklen -1  # to
		if i < N-1:
			parts[i] = data[f:t, :]
		else:
			parts[i] = data[f:,:]

	for i in numpy.arange(0,N):
	        block = parts[i]
		x = block[:,0]
		y = block[:,1]
		p = numpy.polyfit(x,y,1)
		bounds[i] = [ x[1], x[-1] ]
		coeff[i] = [ p[0], p[1] ]

	return bounds, coeff


def gett(eps,tpps,einterp):
	"""
	Get nearest time corresponding to eps. This is done by finding the
	closest value to eps in einterp and returning the corresponding
	value for time.
	"""
	arg = numpy.argmin( numpy.abs( einterp - eps ) )
	return tpps[arg]

def calculateThetaRad(ax,ay,bx,by):
	"""
	Calculating theta as radians with given end point coordinates.
	"""
	thetaIsMoreThanPi = False

	# Is theta > pi or not? In other words, is A point in the
	# left side compared to B?

	if (ax < bx):
		thetaIsMoreThanPi = True

	# Separating case 90 deg (where tan(theta) is infinite). In this, smallNumber
	# is a small, positive number, used for looking for (by-ay) that goes too
	# close to 0 (and, thus, (bx-ax)/(by-ay) goes to infinity).

	smallNumber = 0.000001
	if (abs(by-ay)<smallNumber):
		return pi/2

	thetaR = atan((bx-ax)/(by-ay))

	# Now theta is between [-90,90].
	# Now putting [-90,0] degrees to [90,180].
	if (thetaR < 0):
		thetaR = thetaR + pi

	# Not theta is between [0,180]
	# If theta > pi, we add one pi.
	if thetaIsMoreThanPi:
		thetaR = thetaR + pi

	return thetaR

def calculateFixedThetaRad(ax,ay,bx,by,refOrFat):
	"""
	Calculating theta as radians with given end point coordinates. This time,
	fatigued samples are fixed with SCALE.
	"""

	scale = 1.0
	if refOrFat == "F":
		scale = SCALE

	# REST OF THIS IS ALMOST COPYPASTE FROM calculateThetaRad function!
	# Check the SCALE PART where separately!
	thetaIsMoreThanPi = False

	# Is theta > pi or not? In other words, is A point in the
	# left side compared to B?

	if (ax < bx):
		thetaIsMoreThanPi = True

	# Separating case 90 deg (where tan(theta) is infinite). In this, smallNumber
	# is a small, positive number, used for looking for (by-ay) that goes too
	# close to 0 (and, thus, (bx-ax)/(by-ay) goes to infinity).

	smallNumber = 0.000001
	if (abs(by-ay)<smallNumber):
		return pi/2

	# ATTENTION! Here is scale.
	thetaR = atan((bx-ax)/(by-ay)/scale)

	# Now theta is between [-90,90].
	# Now putting [-90,0] degrees to [90,180].
	if (thetaR < 0):
		thetaR = thetaR + pi

	# Not theta is between [0,180]
	# If theta > pi, we add one pi.
	if thetaIsMoreThanPi:
		thetaR = thetaR + pi

	return thetaR

def calculateThetaDeg(thetaRad):
	"""
	Converting thetaR from radians to degrees
	"""
	theta2 = thetaRad * 180.0/(pi)
	return theta2


def mirrorTheta(thetaRad):
	"""
	Mirroring theta between [-pi/2,pi/2], called theta_m
	(theta mirrored). We presume that the given theta is
	between [0,2*pi]. With abs() function, we get theta
	between [0,90], called theta_mm (theta mirrored mirrored).
	"""
	if (thetaRad < pi/2):
		return thetaRad
	elif (thetaRad < pi):
		return pi - thetaRad
	elif (thetaRad < (3*pi/2)):
		return pi - thetaRad
	else:
		return thetaRad - 2.0*pi

# Read filenames, fatigue times etc of the experiments.
lines = numpy.loadtxt("dict.csv",dtype="string",comments='#',delimiter=',')
fnData = {}
dictlen = lines.shape[1]

for i in range(lines.shape[0]):
	# ATTENTION WITH INDEXES!
	fn=lines[i, 0].strip()
	fatigue=lines[i, 1].strip()
	xdimension=float(lines[i,2].strip()) 
	ydimension=float(lines[i,3].strip()) 
	zdimension=float(lines[i,4].strip()) 
	ax=float(lines[i,5].strip()) 
	ay=float(lines[i,6].strip()) 
	bx=float(lines[i,7].strip()) 
	by=float(lines[i,8].strip()) 
	r_0=float(lines[i,9].strip()) 
	isTidyCurve = lines[i,11].strip() 
	comment = lines[i,dictlen-1].strip() 
	
	dictionaryData=[fatigue,xdimension,ydimension,zdimension,ax,ay,bx,by,r_0,isTidyCurve,comment] 
		# Later remember that the indexes change when moving
		# from the string to the dictionary! For example,
		# the fatigue time is in the list 0, not 1, x dimension
		# is 1, not 2, etc.
	fnData[fn]=dictionaryData 

# This is the list of files to process
fnList = fnData.keys()
fnList.sort()

# We don't necessarily want overwrite old results
if os.path.exists('yield.csv'):
	saveToFile = False
else:
	saveToFile = True
	file = open("yield.csv", 'w')
	firstline="refOrFat, isTidy, filename, fatigue_[s], t_0_[s], theta_[deg], theta_mm_[deg], theta_fixmm_[deg], theta_mm_diff_[deg], r_[mm], eps_0_[%], eps_E_[%], sig_E_[MPa], der_max_[MPa/%], eps_y_[%], sig_y_[MPa], t_y_[s], slope1_[MPa/%], slope2_[MPa/%], comment\n"
	file.write(firstline)

# Remains from Seppala's version...
#
# There was a bug in the labview program saving the TTM data. The data
# was saved partially in engineering units. For this script to work
# after the switch to correct units, we need to read the conversion
# factors necessary for this measurement's data in case the data is
# not in SI units. If conversion.csv exists, it will cotain the
# conversion factors; if not, the data is already in SI units. The
# format of the file is:
#   1st line:s1,s2,s3
#   2nd line:fs1,fs2,fs3
# where values on first line are engineering unit conversion factors
# and values on the second line are the full scale constants

if os.path.exists('conversion.csv'):
	lines=numpy.loadtxt('conversion.csv', dtype="string")
	forceFactor = float(lines[1].split(',')[1]) / float(lines[0].split(',')[1])
	dPosFactor  = float(lines[1].split(',')[2]) / float(lines[0].split(',')[2])
else:
	forceFactor = 1000.0 # kN -> N
	dPosFactor  = 1000.0

if not os.path.exists('plots'):
	os.mkdir('plots')


fnnum = 1

for fn in fnList:
	print fn
	data = numpy.loadtxt(fn)
	
	# Is it Ref or Fat? Is it tidy curve or not?
	# And comments.

	refOrFat = fn[19].capitalize()
	isTidyCurve = fnData[fn][9].capitalize()
	comment = fnData[fn][-1]

	# Calculate theta, theta_m (mirrored [-90, 90])
	# and theta_mm (mirrored [0, 90]) in degrees.
	ax=fnData[fn][4]
	ay=fnData[fn][5]
	bx=fnData[fn][6]
	by=fnData[fn][7]
	thetaR = calculateThetaRad(ax,ay,bx,by)
	thetaD = calculateThetaDeg(thetaR)

	thetaMRad = mirrorTheta(thetaR)			# Theta_m
	thetaMDeg = calculateThetaDeg(thetaMRad)
	thetaMirrorMirrorDeg = abs(thetaMDeg)		# Theta_mm
	thetaFixedMMDeg = abs(calculateThetaDeg( mirrorTheta( calculateFixedThetaRad(ax,ay,bx,by,refOrFat) ) )) # Fixed theta_mm

	# Calculate r in millimeters.
	
	r_0=fnData[fn][8]
	r = abs(r_0/sin(thetaR))

	# F -> stress
	surfaceArea = fnData[fn][1]*fnData[fn][2]/(10**6)
	data[:,1] = -data[:,1] * forceFactor / surfaceArea
	
	# Drop off the points after max stress, in other words,
	# after the 1000 Newton limit trips.
	sig_max_ind = numpy.argmax(data[:,1])
	data = data[:sig_max_ind,:]

	# d -> epsilon
	sampleHeight = fnData[fn][3]
	data[:,2] = -data[:,2]*dPosFactor
	data[:,2] = 100 * (data[:,2] - data[0,2]) / sampleHeight

	# interpolate data
	t = numpy.arange(0,data.shape[0])
	tpps = numpy.arange(0,data.shape[0],(RAWPPS/PPS))
	einterp = numpy.interp(tpps,t,data[:,2])
	sinterp = numpy.interp(tpps,t,data[:,1])
	tpps = tpps / RAWPPS # Now in seconds
	
	# Find e_0 etc:
	msinterp = sinterp.copy()
	monotonize(msinterp)
	# Calculating normal and monotonized difference in each data point
	diff  = (  sinterp[LAG:] -  sinterp[:-LAG] ) / ( einterp[LAG:] - einterp[:-LAG] ) 
	mdiff = ( msinterp[LAG:] - msinterp[:-LAG] ) / ( einterp[LAG:] - einterp[:-LAG] )
	min_t   = gett(SED,tpps,einterp)
	min_ind = min_t*PPS
	mdiff[:min_ind] = mdiff[:min_ind]*0.0 # Drop SED % of strain
	der_max_ind = numpy.argmax(mdiff[:int(len(diff)/4)])
	der_max     = diff[der_max_ind]	
	eps_E       = einterp[der_max_ind]
	sig_E       = sinterp[der_max_ind]
	const       = sig_E - der_max*eps_E
	eps_0       = -const/der_max
	t_0         = gett(eps_0, tpps, einterp) # t closest to eps_0
	t_E         = gett(eps_E, tpps, einterp)
	
	
	# Find the yield point (eps_y, sig_y)
	linapp  = einterp*der_max + const
	yld_ind = (linapp >= 1.1*sinterp)
	eps_y   = numpy.extract(yld_ind,einterp)[0]
	sig_y   = numpy.extract(yld_ind,sinterp)[0]
	t_y     = gett(eps_y, tpps, einterp)

	# Find slope of the "plateu" part of the curves
	XY = numpy.concatenate( ( numpy.row_stack(einterp-eps_0),
				  numpy.row_stack(sinterp)     ), 1)
	bounds, coeff = polylin(XY, NUM_LIN_FITS)

	# Save data
	if saveToFile==True:
		# First save "fatigue vs" data
		fat = int(fnData[fn][0])
		# Creating a printable string. refOrFat and isTidyCurve were  put before the
		# file name to ease manual sorting in SpreadSheet. Commas (,) are needed, because
		# otherwise at least the OpenOffice.org SpreadSheet can't understand that %e's
		# are numbers (not text), and it includes nasty mechanically unfindable apostrophes
		# (') to the file... Before you start to use the data in SpreadSheet, remove commas
		# by selecting the whole grid, then by using Edit -> Find & Replace. The numbers
		# should transform automatically into the right form.
		sf = "%s, %s, %s, %d, %e, %e, %e, %e, %e, %e, %e, %e, %e, %e, %e, %e, %e, %e, %e, %s\n" % (refOrFat, 
							       isTidyCurve,
							       fn.split("_")[1],	# First time stamp away
							       fat,
							       t_0,
							       thetaD,
							       thetaMirrorMirrorDeg,
							       thetaFixedMMDeg,
							       abs(thetaMirrorMirrorDeg-thetaFixedMMDeg),
							       r,			# Millimeters
							       eps_0,			# Percents
							       eps_E,			# Percents
							       sig_E/1000000.0, 	# From Pa to MPa
							       der_max*(1/1000000.0),	# From Pa/% to MPa/%
							       eps_y,			# Percents
							       sig_y/1000000.0, 	# From Pa to MPa
							       t_y,
							       coeff[1][0]*(1/1000000.0), # From Pa/% to MPa/%
							       coeff[2][0]*(1/1000000.0), # From Pa/% to MPa/%
							       comment)
		file.write(sf)

		stringAngleMm = "%.2f" % thetaMirrorMirrorDeg

		# Cropping the file name shorter. Contains now only the name of the sample and
		# its theta_mm angle. For making legend bar cleaning notably easier...

		saveNamePhase1 = fn.split('.dat')[0] # .dat away
		saveNamePhase2 = saveNamePhase1.split("_")[1] # First timestamp away
		saveNameFin = saveNamePhase2[0:9]

		# Then the interpolated & eps_0 translated data 
		sf = saveNameFin + "_" + stringAngleMm + "-interp.csv"
		out = numpy.array(zip(einterp-eps_0, sinterp), dtype='float')
		numpy.savetxt(sf, out, fmt='%f, %f')

		# Saving the same data with scaling sinterp/1000000 to make the
		# plots look nicer.
		sf = saveNameFin + "_" + stringAngleMm + "-interpScale.csv"
		out = numpy.array(zip(einterp-eps_0, sinterp/1000000.0), dtype='float')
		numpy.savetxt(sf, out, fmt='%f, %f')

		# And the slopes
		sf = saveNameFin + "_" + stringAngleMm + "-slopes.csv"
		numpy.savetxt(sf, coeff, fmt='%f, %f') # slope, intercept !


        # Plots
        mpl.figure(1)
        mpl.plot(einterp-eps_0,sinterp,label=fn)

        # Single curve plots with linear fit overlays
        fig = mpl.figure(3)
        fig.clf()
        ax = fig.add_subplot(111)

        mpl.plot(einterp-eps_0,sinterp,label=fn)

        fnnum = fnnum + 1
        for i in numpy.arange( 0, len(coeff) ):
                x = numpy.array(bounds[i]) 			# Taking the start and the end points of i:s area.
                y = x.copy() * coeff[i][0] + coeff[i][1] 	# y = a*x + b
                mpl.plot( x, y, 'k-', linewidth=2) 		# Plotting it onto the picture.
        for i in numpy.arange( 0, len(coeff) ):
                x = numpy.array(bounds[i])
                mpl.plot([x[0],x[0]],[0,1.4*1e7], 'k:')		# Putting vertical dashed lines between the areas.
        mpl.plot([x[1],x[1]],[0,1.4*1e7], 'k:')			# Putting the last dashed line.
        
        bbox_props = dict(boxstyle="rarrow,pad=0.3", fc="white", ec="b", lw=2)

        textX = ( bounds[1][0] + bounds[1][1] ) / 2
        textY = (textX * coeff[1][0] + coeff[1][1]) + 2.5e6
        t = ax.text(textX, textY, "1", ha="center", va="center", rotation=-90,
            size=15,
            bbox=bbox_props)

        textX = ( bounds[2][0] + bounds[2][1] ) / 2
        textY = (textX * coeff[2][0] + coeff[2][1]) + 2.5e6
        t = ax.text(textX, textY, "2", ha="center", va="center", rotation=-90,
            size=15,
            bbox=bbox_props)

        titlestr = fn[13:22]

        ax.annotate(titlestr, xy=(.5, .975),
                    xycoords='figure fraction',
                    horizontalalignment='center', verticalalignment='top',
                    fontsize=20)

        locs, labels = mpl.yticks([0, 2e+6, 4e+6, 6e+6, 8e+6, 1e+7, 1.2e+7, 1.4e+7],
                                  ['0', '2', '4', '6', '8', '10', '12', '14'],
                                  fontsize=15)
        locs, labels = mpl.xticks(fontsize=15)

        mpl.xlabel(r'Puristuma $\epsilon$ [%]', {'color'    : 'k',
                                              'fontsize'   : 25 })
        mpl.ylabel(r'Rasitus $\sigma$ [MPa]', {'color'    : 'k',
                                                'fontsize'   : 25 })

        # And axis limits
        mpl.ylim(0,1.4e7)
        mpl.xlim(numpy.min(einterp-eps_0),numpy.max(einterp-eps_0))
        
        # Save the single-plots
        fname = "plots/%s_stess-strain_with_fits.pdf" % titlestr
        mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
                    orientation='portrait', format='pdf',
                    transparent=False, bbox_inches=None, pad_inches=0.1)

        # Plots pf the e_0 etc

        fig = mpl.figure(4)
        fig.clf()
        mpl.plot(einterp,sinterp/1000000.0,'k-')
        mpl.plot(einterp,1.1*sinterp/1000000.0,'g-')
        extx = numpy.array([eps_0,eps_y])
        exty = numpy.array([eps_0,eps_y])*der_max+const
        mpl.plot(extx, exty/1000000.0, 'ko--', linewidth=2)
        mpl.plot([eps_0],[0], 'go')
        mpl.plot([eps_E],[sig_E/1000000.0], 'bo')
        mpl.plot([eps_y], [sig_y/1000000.0], 'ro')
        fname = "plots/%s_eps0_etc.pdf" % titlestr
        arg = numpy.argmin( numpy.abs( einterp - 2*eps_y ) )

        mpl.xlabel(r'Puristuma $\epsilon$ [%]', {'color'    : 'k',
                                              'fontsize'   : 25 })
        mpl.ylabel(r'Rasitus $\sigma$ [MPa]', {'color'    : 'k',
                                                'fontsize'   : 25 })
        ax.annotate("", xy=(.5, .975),
                    xycoords='figure fraction',
                    horizontalalignment='center', verticalalignment='top',
                    fontsize=20)

        mpl.xlim(0,einterp[arg])
        mpl.ylim(0,1.5*sinterp[arg]/1000000.0)
        mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
                    orientation='portrait', format='pdf',
                    transparent=False, bbox_inches=None, pad_inches=0.1)

		

if saveToFile==True:
	file.write("fat, ref")
	file.close()
else:
	print "'yield.csv' already exists! Data not saved!"


# Change the default legend font size
mpl.matplotlib.rcParams['legend.fontsize']=8

mpl.figure(1)
mpl.xlabel("Strain [%]")
mpl.ylabel("Stress [N/m^2]")
mpl.legend(loc="upper left")
mpl.xlim(-5,60)
# The following sets line colors of all curves to (slightly) different
# colors. This trick doesn't work very well with too many lines as
# they become impossible to tell apart by color.
mpl.gca().set_color_cycle([mpl.cm.spectral(i) for i in numpy.linspace(0, 0.9, len(fnList))])

fname = "plots/zAll.pdf"
mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
                    orientation='portrait', format='pdf',
                    transparent=False, bbox_inches=None, pad_inches=0.1)
