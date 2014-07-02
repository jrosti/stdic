import scipy
import scipy.linalg as linalg
import pylab as plt
import numpy
import scipy.linalg.basic
import mgrant
#from scipy.optimize import curve_fit
from scipy.optimize import *

def fit_linlogtc(points, tc):
	xdata = points[:,0]
	ydata = points[:,1]
	matrix = []
	for x in xdata:
		matrix.append([numpy.log(x), 1/(tc-x),1.0]) # for y = a ln(x) + b/(t_c - t)+c
	coeffs = scipy.linalg.basic.lstsq(matrix, ydata)[0]
	print "yields:  x data     y data    calc value   error"
	error = 0.0
	print "Fitting information from linlsq"
	for i in range(len(xdata)):
		ycalc = coeffs[0] * numpy.log(xdata[i]) + coeffs[1] * 1 / (tc - xdata[i]) + coeffs[2]
		error = ycalc - ydata[i]
		print "         % .3f    % .3f      % .3f    % .3f" % (xdata[i], ydata[i], ycalc, error)
	ymodel = []
	xr = numpy.arange(xdata[0], xdata[-1], 0.1)
	for x in xr:
		ycalc = coeffs[0] * numpy.log(x) + coeffs[1] * 1 / (tc - x) + coeffs[2]
		ymodel.append(ycalc)
	plt.plot(xdata,ydata,'o',linewidth=0)
	plt.plot(xr, ymodel,linewidth=3)
	plt.savefig('linlogtc.png')
	return (coeffs,numpy.array(ymodel), error)

def func(x, a,b,c,d,e):
	value = a*x**b +c + e/(d-x)
	return value

def fit_generalfunc(points):
	xdata = points[:,0]
	ydata = points[:,1]
	print xdata, ydata
	popt, pcov = my_curve_fit(func, xdata, ydata, p0=(1,0.3,0,1260,3))
	xr = numpy.arange(xdata[0], xdata[-1], 0.1)
	ymodel = []
	for x in xr:
		ymodel.append(func(x,*popt))
	print popt[0], popt[1], popt[2], popt[3], popt[4]
	plt.plot(xr, ymodel, linewidth=3)
	plt.savefig('generalfunc.png')
	return 0.0

def _general_function(params, xdata, ydata, function):
	return function(xdata, *params) - ydata


def _weighted_general_function(params, xdata, ydata, function, weights):
	return weights * (function(xdata, *params) - ydata)

def my_curve_fit(f, xdata, ydata, p0=None, sigma=None, **kw):
	if p0 is None or numpy.isscalar(p0):
		# determine number of parameters by inspecting the function
		import inspect
		args, varargs, varkw, defaults = inspect.getargspec(f)
		if len(args) < 2:
			msg = "Unable to determine number of fit parameters."
			raise ValueError(msg)
		if p0 is None:
			p0 = 1.0
		p0 = [p0]*(len(args)-1)

	args = (xdata, ydata, f)
	if sigma is None:
		func = _general_function
	else:
		func = _weighted_general_function
		args += (1.0/asarray(sigma),)
	res = leastsq(func, p0, args=args, full_output=1, **kw)
	(popt, pcov, infodict, errmsg, ier) = res
	if ier != 1:
		msg = "Optimal parameters not found: " + errmsg
		raise RuntimeError(msg)
	if (len(ydata) > len(p0)) and pcov is not None:
		s_sq = (func(popt, *args)**2).sum()/(len(ydata)-len(p0))
		pcov = pcov * s_sq
	else:
		pcov = inf
	return popt, pcov
