""" Module bigpyramid implements a B-spline pyramid with on-demand
    generated coarser levels

    Jan Kybic, October 2000
    $Id: bigpyramid.py,v 1.1 2005/10/07 15:45:06 eav Exp $
"""

import bigsplines    # import B-spline routines
import BIGsplines    # import B-spline routines in C
import bigtools
import math
from numpy import *

# ----------------------------------------------------------------------

def binomfilt(n):
    """ Returns a binomial kernel (1+z)^(n+1)/2^n as an array.
        The second parameter returned is the kernel origin, ready for the
        call to BIGsplines.FirConvolve. When the kernel has even length, the
        kernel origin is shifted left """
    try:
        kernel,denom=(((1,1),1),                     # n=0
                  ((1,2,1),2),                       # n=1
                  ((1,3,3,1),4),                     # n=2
                  ((1,4,6,4,1),8),                   # n=3
                  ((1,5,10,10,5,1),16),              # n=4
                  ((1,6,15,20,15,6,1),32),           # n=5
                  ((1,7,21,35,35,21,7,1),64),        # n=6
                  ((1,8,28,56,70,56,28,8,1),128))[n] # n=7
    except IndexError:
        raise BIGsplines.error, 'Degree %d not available' % degree
    kernelorig=(len(kernel)-1)/2
    kernel=reshape(array(kernel),(-1,))/math.pow(2,n)
    return kernel, kernelorig


# ----------------------------------------------------------------------

def bsreduce(c,degree,bcond=bigsplines.defaultbcond):
    """ Given a 1D array of B-spline coefficients
        c, make a half resolution version cr, optimal in the L2 sense

        See Unser, Aldroubi, Eden: The L2 Polynomial Spline Pyramid,
        IEEE Trans. on Pattern Analysis and Machine Intelligence,
        vol. 15, no. 4, April 1993
        """
    if bcond!=bigsplines.TBoundaryConvention['MirrorOnBounds']:
        raise "Unsupported boundary convention"

    c=bigsplines.firspline(c,2*degree+1,bcond=bcond)   # go to the dual space
    kernel,kernelorig=binomfilt(degree)
    c=BIGsplines.FirConvolve(c,kernel,kernelorig,bcond)/2.0   # binomial filter
    c=bigtools.downsample(c,2)
    c=bigsplines.fspline(c,2*degree+1,bcond=bcond)        # back to B-spline sp.
    return c

# --------------------------------------------------------------------

def bsexpand(c,degree,bcond=bigsplines.defaultbcond):
    """ Given a 1D array of B-spline coefficients c,
        make a double resolution version representing the same function.

        Note that MirrorOnBoundary boundary conditions would impose that the
        expand of n-point vector has (2n-1) points which is inconvenient.

        See Unser, Aldroubi, Eden: The L2 Polynomial Spline Pyramid,
        IEEE Trans. on Pattern Analysis and Machine Intelligence,
        vol. 15, no. 4, April 1993
        """
    if bcond!=bigsplines.TBoundaryConvention['MirrorOnBounds']:
        raise "Unsupported boundary convention"
    kernel,kernelorig=binomfilt(degree)
    c=bigtools.upsample(c,2)[:-1] # leave out [:-1] if you want exact expand
    c=BIGsplines.FirConvolve(c,kernel,kernelorig,bcond)      # binomial filter
    return c

# --------------------------------------------------------------------

def mbsreduce(c,degree,bcond=bigsplines.defaultbcond):
    """ Given a multidimensional array of B-spline coefficients c,
        return a half resolution version by applying bsreduce to
        all dimensions."""
    return bigsplines.applyseparablewithcopy(c,
                          lambda inp,d=degree,bcond=bcond:
                                             bsreduce(inp,d,bcond=bcond) )

# --------------------------------------------------------------------

def mbsexpand(c,degree,bcond=bigsplines.defaultbcond):
    """ Given a multidimensional array of B-spline coefficients c,
        return a double resolution version by applying bsexpand to
        all dimensions."""
    return bigsplines.applyseparablewithcopy(c,
                          lambda inp,d=degree,bcond=bcond:
                                             bsexpand(inp,d,bcond=bcond) )

# --------------------------------------------------------------------


class BSPyramid:
    """ An instance of BSPyramid is initialized with an n-dimensional
        image. Subsequent queries for lower-resolution versions 
        are calculated if needed and cached for later """
    
    cpyr=[] # an empty list of coefficients
    ppyr={} # an empty dictionary of images

    def __init__(self,image,degree=3): # constructor
        self.degree=degree
        self.ppyr={ 0 : asarray(image,Float) }
        self.cpyr=[ bigsplines.mfspline(self.ppyr[0],self.degree) ]

    def getcoefs(self,level):    # level=0 original, 1 half size, ...
        if len(self.cpyr)<=level: # coefs not yet cached
            self.cpyr.append(mbsreduce(self.getcoefs(level-1),self.degree))
        return self.cpyr[level]
        

    def getimage(self,level):    # level=0 original, 1 half size, ...
        if not self.ppyr.has_key(level): # image not yet cached
            self.ppyr[level]=bigsplines.mfirspline( # calculate image
                self.getcoefs(level),self.degree) 
        return self.ppyr[level]

# --------------------------------------------------------------------

def test_updownsample():
    x=array((1,2,3,4))
    u=bigtools.upsample(x,2)
    d=bigtools.downsample(u,2)
    print "x=",x,"u=",u,"d=",d

def test_expandreduce():
    x=array((1,2,3,4,5,6,7,8,9,10))
    c=bigsplines.fspline(x,3)
    cx=bigsplines.firspline(c,3)
    cr=bsreduce(c,3)
    xr=bigsplines.splineinterpol(cr,reshape(array((0,0.5,1,1.5,2)),(1,-1)),3)
    ce=bsexpand(c,3)
    xe=bigsplines.firspline(ce,3)
    print "x=",x
    print "c=",c
    print "cx=",cx
    print "cr=",cr
    print "xr=",xr
    print "ce=",ce
    print "xe=",xe   
    cer=bsreduce(ce,3)
    xer=bigsplines.firspline(cer,3)
    print "xer=",xer

def test_mexpandreduce():
    import Image
    #import NumTut
    import time
    import bigtools
#    im=Image.open('/home/jkybic/matlab/images/lena.tiff')
    im=Image.open('lena.tiff')
    ima=bigtools.ImageToArray(im)
    print ima.shape
    # NumTut.view(ima)
    t1=time.time()
    cima=bigsplines.mfspline(ima,3)
    print "B-spline transform took", time.time()-t1, " s"
    t1=time.time()
    cir=mbsreduce(cima,3)
    print "Reduction took", time.time()-t1, " s"
    t1=time.time()
    ir=bigsplines.mfirspline(cir,3)
    print "B-spline interpolation took", time.time()-t1, " s"
    v1=bigtools.view(ir)
    t1=time.time()
    cire=mbsexpand(cir,3)
    print "Expansion took", time.time()-t1, " s"
    t1=time.time()
    ire=bigsplines.mfirspline(cire,3)
    print "B-spline interpolation took", time.time()-t1, " s"
    v2=bigtools.view(ire)
    print ire.shape
    dim=abs(ire-ima)
    v3=bigtools.view(dim)
    print maximum.reduce(maximum.reduce(dim))
    raw_input('Press any key')

def test_pyramid():
    import Image
    import NumTut
    import time
#    im=Image.open('/home/jkybic/matlab/images/lena.tiff')
    im=Image.open('lena.tiff')
    ima=bigsplines.ImageToArray(im)
    print ima.shape
    p=BSPyramid(ima)
    q=p.getimage(3)
    print q.shape
    NumTut.view(q)
    q=p.getimage(3)
    print q.shape
    NumTut.view(q)
    q=p.getcoefs(3)
    print q.shape
    NumTut.view(q)


if __name__=='__main__': # running interactively
    # test_updownsample()
    # test_expandreduce()
    # test_mexpandreduce()
    test_pyramid()
