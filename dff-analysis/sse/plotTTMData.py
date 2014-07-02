import numpy
import os
from glob import glob
import matplotlib.pyplot as mpl
from scipy import stats as sp

# This sript assumes that the raw TTM data is stored at the current
# working directory (CWD) when it it executed. The raw data should be
# named in the following way:
# "201103221201_11032203-R1A10-7.dat"
# where "201103221201" is the date saved by labview, "11032203" is the
# measurement date and number of measurement (NN) in the format
# YYMMDDNN, and R1A10 is the fatigue geometry and 7 is the sample
# number/name. Note that the script won't work unless the filenames
# are as specified.
#
# In addition to the data files, a
# comma separated list of data files (.dat!) and fatigue times is
# expected to be found in dict.csv. The format is
# dataFileName1.dat,0
# dataFileName2.dat,12
# and so on. Empty lines in dict.csv will probably cause problems.
#
# This script writes:
# a) yield points and other similar data to yield.csv
# b) interpolated stress-strain data to dataFilename-interp.csv
# c) coefficents of linear fits to dataFileName-slopes.csv
# d) plots of the linear fits are saved in the subdirectory plots/
#
# Please note that in a) none of the values are translated by eps0
# and that all of the interpolated data b) is translated left by eps0!

### CONSTANTS ################################################
RAWPPS        = 500.0                # pps in the raw data   #
PPS           = 10.0                 # pps to interpolate to #
LAG           = 3.0*PPS              # 5 s lag ~= 1.7% strain#
SURFACE_AREA  = 6.0 * 12.0 / (10**6) # m^2                   #
SAMPLE_HEIGHT = 6.0                  # mm                    #
SED           = 0.5                  # skip % of mdiff       #
NUM_LIN_FITS  = 4                    # # of fits for slopes  #
##############################################################

# RAWPPS is the sample rat in the raw data files
# PPS is the sample rate to which the data is interpolated.
# LAG is the lag used in the numerical derivatives
# SURFACE AREA is the surface area of the samples facing the
#              compression plate
# SAMPLE_HEIGHT is the height of the samples in millimetres
# SED is the ammount of strain to skip when looking for steepest part
#     of the stress strain curve (young's modulus)
# NUM_LIN_FITS is the ammount of straights to try to fit into the
#              stress strain curves in order to obtain the plateu
#              slope. The number 4 seems to work pretty well.

# Make list non-decreasing (not really monotonic strictly speaking)
def monotonize(list):
	for i in range(0,len(list)-1):
		if list[i] > list[i+1]:
			list[i+1] = list[i]

# Fit N straights to evenly divided parts of data.  The data should be
# of the form [ X, Y ] where X and Y are column vectors.
def polylin(data,N):
	coeff  = [numpy.array([])] * N
	bounds = [numpy.array([])] * N
	parts  = [numpy.array([])] * N
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
		slope, intercept, r_value, p_value, std_err = sp.linregress(x,y)
		bounds[i] = [ x[1], x[-1] ]
		coeff[i] = [ slope, intercept ]

	return bounds, coeff

# Get nearest time corresponding to eps. This is done by finding the
# closest value to eps in einterp and returning the corresponding
# value for time.
def gett(eps,tpps,einterp):
	arg = numpy.argmin( numpy.abs( einterp - eps ) )
	return tpps[arg]


# Read filenames and fatigue times of the experiments
lines = numpy.loadtxt("dict.csv",dtype="string")
fatigues = {}
for i in range(lines.shape[0]):
	fn=lines[i].split(',')[0]
	fatigue=lines[i].split(',')[1]
	fatigues[fn]=fatigue

# This is the list of files to process
fnList = fatigues.keys()
fnList.sort()

# We don't necessarily want overwrite old results
if os.path.exists('yield.csv'):
	saveToFile = False
else:
	saveToFile = True
	file = open("yield.csv", 'w')
	firstline="filename, fatigue, t_0, eps_0, eps_E, sig_E, der_max, eps_y, sig_y, slope1, slope2\n"
	file.write(firstline)

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
	forceFactor = 1
	dPosFactor  = 1000

if not os.path.exists('plots'):
	os.mkdir('plots')


fnnum = 1

for fn in fnList:

	print fn
	
	data = numpy.loadtxt(fn)

	# F -> stress
	data[:,1] = -data[:,1] * forceFactor / SURFACE_AREA
	
	# Drop off the points after max stress
	sig_max_ind = numpy.argmax(data[:,1])
	data = data[:sig_max_ind,:]

	# d -> epsilon
	data[:,2] = -data[:,2]*dPosFactor
	data[:,2] = 100 * (data[:,2] - data[0,2]) / SAMPLE_HEIGHT

	# interpolate data
	t = numpy.arange(0,data.shape[0])
	tpps = numpy.arange(0,data.shape[0],(RAWPPS/PPS))
	einterp = numpy.interp(tpps,t,data[:,2])
	sinterp = numpy.interp(tpps,t,data[:,1])
	tpps = tpps / RAWPPS # Now in seconds
	
	# Find e_0 etc
	msinterp = sinterp.copy()
	monotonize(msinterp)
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
		fat = int(fatigues[fn])
		sf = "%d, %e, %e, %e, %e, %e, %e, %e, %e, %e\n" % (fat,
							       t_0,
							       eps_0,
							       eps_E,
							       sig_E,
							       der_max,
							       eps_y,
							       sig_y,
							       coeff[1][0],
							       coeff[2][0])
		sf = fn + ", " + sf
		file.write(sf)

		# Then the interpolated & eps_0 translated data 
		sf = fn.split('.dat')[0] + "-interp.csv"
		out = numpy.array(zip(einterp-eps_0, sinterp), dtype='float')
		numpy.savetxt(sf, out, fmt='%f, %f')

		# And the slopes
		sf = fn.split('.dat')[0] + "-slopes.csv"
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
		x = numpy.array(bounds[i])
		y = x.copy() * coeff[i][0] + coeff[i][1]
		mpl.plot( x, y, 'k-', linewidth=2)
	for i in numpy.arange( 0, len(coeff) ):
		x = numpy.array(bounds[i])
		mpl.plot([x[0],x[0]],[0,1.4*1e7], 'k:')
	mpl.plot([x[1],x[1]],[0,1.4*1e7], 'k:')
	
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

	titlestr = fn.split('-')[1] + " " + fn.split('-')[2].split('.dat')[0] + " fatigue time: " + fatigues[fn] + " s"
	ax.annotate(titlestr, xy=(.5, .975),
		    xycoords='figure fraction',
		    horizontalalignment='center', verticalalignment='top',
		    fontsize=20)

	locs, labels = mpl.yticks([0, 2e+6, 4e+6, 6e+6, 8e+6, 1e+7, 1.2e+7, 1.4e+7],
				  ['0', '2', '4', '6', '8', '10', '12', '14'],
				  fontsize=15)
	locs, labels = mpl.xticks(fontsize=15)

	mpl.xlabel(r'Strain $\epsilon$ [%]', {'color'    : 'k',
					      'fontsize'   : 25 })
	mpl.ylabel(r'Stress $\sigma$ [MPa]', {'color'    : 'k',
						'fontsize'   : 25 })

	# And axis limits
	mpl.ylim(0,1.4e7)
	mpl.xlim(numpy.min(einterp-eps_0),numpy.max(einterp-eps_0))
	
	# Save the single-plots
	fname = "plots/%s_stess-strain_with_fits.pdf" % fn.split('.dat')[0]
	mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
		    orientation='portrait', format='pdf',
		    transparent=False, bbox_inches=None, pad_inches=0.1)

	# Plots pf the e_0 etc

	fig = mpl.figure(4)
	fig.clf()
	mpl.plot(einterp,sinterp,'k-')
	mpl.plot(einterp,1.1*sinterp,'g-')
	extx = numpy.array([eps_0,eps_y])
	exty = numpy.array([eps_0,eps_y])*der_max+const
	mpl.plot(extx, exty, 'ko--', linewidth=2)
	mpl.plot([eps_0],[0], 'go')
	mpl.plot([eps_E],[sig_E], 'bo')
	mpl.plot([eps_y], [sig_y], 'ro')
	fname = "plots/%s_eps0_etc.pdf" % fn.split('.dat')[0]
	arg = numpy.argmin( numpy.abs( einterp - 2*eps_y ) )
	mpl.xlim(0,einterp[arg])
	mpl.ylim(0,1.5*sinterp[arg])
	mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
		    orientation='portrait', format='pdf',
		    transparent=False, bbox_inches=None, pad_inches=0.1)
	
	
if saveToFile==True:
	file.close()
else:
	print "'yield.csv' already exists! Data not saved!"

# Change the default legend font size
mpl.matplotlib.rcParams['legend.fontsize']=8

mpl.figure(1)
mpl.xlabel("Strain [%]")
mpl.ylabel("Stress [N/m^2]")
mpl.legend(loc="upper left")
mpl.ylim(0,1000/SURFACE_AREA)
mpl.xlim(-5,60)
# The following sets line colors of all curves to (slightly) different
# colors. This trick doesn't work very well with too many lines as
# they become impossible to tell apart by color.
mpl.gca().set_color_cycle([mpl.cm.spectral(i) for i in numpy.linspace(0, 0.9, len(fnList))])

fname = "plots/all.pdf"
mpl.savefig(fname, dpi=300, facecolor='w', edgecolor='w',
		    orientation='portrait', format='pdf',
		    transparent=False, bbox_inches=None, pad_inches=0.1)


