
""" Module bigsplines provides high level functions
    for spline manipulation functions from
    helper module BIGsplines (implemented in C)


    Jan Kybic, August 2000
    $Id: bigsplines.py,v 1.1 2005/10/07 15:45:06 eav Exp $
"""

from numpy import *
from types import *    # import type names
import BIGsplines      # import the C functions
import sys

# ----------------------------------------------------------------------

# WARNING the following list must be consistent with BIGsplines.h

TBoundaryConvention= { 'AntiMirrorOnBounds': 0,
  'FiniteCoefficientSupport': 1,
  'FiniteDataSupport': 2,
  'MirrorOffBounds': 3,
  'MirrorOnBounds': 4,
  'Periodic':5 }
defaultbcond=TBoundaryConvention['MirrorOnBounds']

# ----------------------------------------------------------------------

# we moved the imports here to take care of dependencies
import bigpyramid
import bigtools


def fspline(x,degree,bcond=defaultbcond):
    """ Given values (x) of a function in points 1,2,...n, 
finds coefficients c, such as for all k=1..n
x(k)=sum  c(i) spline_of_degree_N(k-i),   for i=1..n

i.e., finds B-spline interpolation

degree=0 constant, 1 linear, 2 quadratic ...

References : 
M. Unser, A. Aldroubi and M. Eden, Fast B-spline transforms for
continuous image representation and interpolation, IEEE Trans. Pattern Anal.
Machine Intell., vol. 13, pp. 277-285, March 1991.
M. Unser, A. Aldroubi and M. Eden, B-spline signal processing. Part II :
efficient design and applications, IEEE Trans. Signal Processing, vol. 41,
pp. 834-848, February 1993.

Returns a flat double array
"""
    x=array(x,'d') # make a copy
    # Get types right
    if type(degree)!=IntType:
        degree=int(degree)
    if  degree==0 or degree==1:
        return x # return the same thing
    # Get poles
    try:
        poles=((-3+2*sqrt(2)),(-2+sqrt(3)),           # degrees 2,3
       (-0.361341,-0.0137254),(-0.430575,-0.0430963), # degrees 4,5
       (-0.488295,-0.0816793,-0.00141415),            # degree 6
       (-0.53528,-0.122555,-0.00914869))[degree-2]     # degree 7
    except IndexError:
        raise BIGsplines.error, 'Degree %d not available' % degree
    poles=reshape(array(poles),(-1,)) 
    if len(x.shape)==0:
        x=reshape(x,(-1,)) # make sure we have a 1D array
    elif len(x.shape)>1:
        raise BIGsplines.error, 'Only 1D input is currently supported' % degree

    result=BIGsplines.IirConvolvePoles(x,poles,bcond)
    return result.ravel() # always 1D

# ----------------------------------------------------------------------

def mfspline(x,degree,bcond=defaultbcond):
    """ Finds B-spline interpolation coefficients for multidimensional
        arrays x. Works for any dimensionality.
        Returns a double array of coefs """
    if degree<2: return x  # NOTE: No copy is made here, fast but dangerous
    return applyseparable(x,lambda inp,degree=degree,bcond=bcond:
                          fspline(inp,degree,bcond) )

# ----------------------------------------------------------------------

def mfirspline(c,degree,bcond=defaultbcond):
    """ Finds function values x given B-spline interpolation coefficients
        c. Works for any dimensionality. Returns a double array of values """
    if degree<2: return c  # NOTE: No copy is made here, fast but dangerous
    return applyseparable(c,lambda inp,degree=degree,bcond=bcond:
                          firspline(inp,degree,bcond=bcond) )

# ----------------------------------------------------------------------

def applyseparable(x,oper,passdim=None):
    """ Apply operation oper on all dimensions of an 
        arrays x. Oper should take one argument - a 1D double array and return
        an array of the same size. applyseparable returns a double array

        If passdim is true, the 'oper' is passed a keyword argument
        'ndim' giving the dimension being processed.
        """
    dims=len(x.shape)
    x=array(x,'d') # make a copy and upcast to double if needed
    for d in range(dims): # for all dimensions
        if passdim:
            x=bigtools.applyforallrows(x,oper,ndim=d)
        else:
            x=bigtools.applyforallrows(x,oper)
        x=transpose(x,range(1,dims)+[0]) # shift dimensions
    return x

# ----------------------------------------------------------------------  
    
def applyseparablewithcopy(x,oper,passdim=None):
	"""
		Apply operation oper on all dimensions of an 
		arrays x. Oper should take one argument - a 1D double array and return
		another 1D array not necessarily of the same size.
		applyseparablewithcopy returns a double array.

		If passdim is true, the 'oper' is passed a keyword argument
		'ndim' giving the dimension being processed.
	"""

	x=array(x,'d')
	y=None
	dims = len(x.shape)

	for dim in xrange(dims):
		arrayshape = list(x.shape)
		for i in xrange(arrayshape[1]):
			if passdim:
				row = apply(oper, (x[:,i],),{'ndim':dim})
			else:
				row = apply(oper, (x[:,i],))
			if row.shape[0] != arrayshape[0]:
				arrayshape[0] = row.shape[0]
				y=zeros(arrayshape,'d')
			elif y==None:
				y=zeros(arrayshape,'d')
			y[:,i] = row
		x = y.T

	return x

# ----------------------------------------------------------------------

def correctflag(f,d):
    """ Inverse the order of the axes to pass to the C code for
    splineinterpol and similar routines. d is the number of dimensions. """
    f=(f&3,f&12,f&48)    # mask out components for x,y,z
    if d==1:
        return f[0]
    elif d==2:
        return (f[0]<<2) | (f[1]>>2)
    elif d==3:
        return (f[0]<<4) | f[1] | (f[2]>>4)

    raise BIGsplines.error, "Unexpected d=%d" % d

# ----------------------------------------------------------------------

def bsplnevalfract(k,degree):
    """ Evaluates a B-spline of degree 'degree' at points
        -support+1/k,..,-1/k,0,1/k,..,support-1/k
        Returns a 1D float array 'kern' and the offset of the center point
        """
    bs=BIGsplines.Evalbspln(arange(0,(degree+1)/2.0,1.0/k),degree)
    klen=bs.shape[0] # length of the half-kernel
    kern=zeros((2*klen-1),float) # make the full kernel
    kern[:klen-1]=bs[-1:0:-1]
    kern[klen-1:]=bs
    return kern,klen-1
# ----------------------------------------------------------------------

def splineinterpol(coefs,points,degree,flag=0,
                   bcond=defaultbcond):
    """ a wrapper to BIGsplines.SplineInterpol. It interpolates a function
    given by B-spline coefficients (coefs) at points (points).
    Points can by generated by indices(), coefs by mfspline()
    flag is passed on to BIGsplines.SplineInterpol to interpolate also
    derivatives.
    """

    coefs=ascontiguousarray(coefs,float)
    points=asfarray(points)
    ptshape=points.shape

    if type(points)!=type(array(1)):
        raise BIGsplines.error, "points should be an array"
    dims=len(coefs.shape)
    if points.shape[0]!=dims:
        raise BIGsplines.error, \
              "points.shape[0] is expected to be %d" % dims
    if len(points.shape)!=dims+1:
        raise BIGsplines.error, \
              "Dimension of points is expected to be %d" % (dims+1)
    points=points[::-1,...] # this seems to make an explicit copy
    points=transpose(points,range(1,dims+1)+[0])
    return BIGsplines.SplineInterpol(coefs,points,degree,
                                     correctflag(flag,dims),bcond)

# ----------------------------------------------------------------------


def firspline(c,degree,bcond=defaultbcond):
    """ Given B-spline coefficients (c), calculate the function values (x) 
        x(k)=sum  c(i) spline_of_degree_N(k-i),   for i=1..n

        degree=0 constant, 1 linear, 2 quadratic ...

        Input is scalar. Returns a flat double array
    """
    c=array(c,'d') # make a copy
    # Get types right
    if type(degree)!=IntType:
        degree=int(degree)
    if  degree==0 or degree==1:
        return c # return the same thing
    # Get kernel
    try:
        kernel=((0.125,0.75,0.125),(1.0/6.0,2.0/3.0,1.0/6.0), # degrees 2,3
       (1.0/384,76.0/384,230.0/384,76.0/384,1.0/384),          # degree 4
       (1.0/120,26.0/120,66.0/120,26.0/120,1.0/120),           # degree 5
       (0.00002170138889,0.01566840277778,0.22879774305556,0.51102430555556,
        0.22879774305556,0.01566840277777,0.00002170138893),   # degree 6
       (0.00019841269841,0.02380952380952,0.23630952380952,
        0.47936507936508,0.23630952380952,0.02380952380953,
        0.00019841269840))[degree-2]             # degree 7
    except IndexError:
        raise BIGsplines.error, 'Degree %d not available' % degree
    kernelorig=(len(kernel)-1)/2
    kernel=reshape(array(kernel),(-1,)) 
    if len(c.shape)==0:
        c=reshape(c,(-1,)) # make sure we have a 1D array
    elif len(c.shape)>1:
        raise BIGsplines.error, 'Only 1D input is currently supported' % degree

    result=BIGsplines.FirConvolve(c,kernel,kernelorig,bcond)
    return result.ravel() # always 1D

# ----------------------------------------------------------------------

class MSplineSignal:
    """ Implements multidimensional spline signal defined between
    (0..xmax1)x(0..xmax2)...
    Initialization:
                    s=MSplineSignal(x=signal,c=coefs,xmax=limit,
                                   degree=3,shift=floor(degree/2))

    When neither the signal x, nor its coefficients c are given,
    set it to zero. shift is an integer number of spline knots added
    to the left (and normally also on the right),
    i.e. x(0) coincides with c(shift).

    The x,c, and xmax are supposed to have the same dimensionality
    dim, shift is a scalar.

    The signal can be evaluated, reduced and expanded by two.  Always,
    Reduce(Expand(signal))==signal, the converse conserves the length of
    the signal. The expansion is exact, the reduction is currently done
    in the sense of L2. There is always one spline coefficient centered at
    zero.

    Note that any spline is representable, no boundary conditions come into
    play, except when calculating c from x and when reducing.
    """

    def __init__(self,x=None,c=None,xmax=None,degree=3,shift=None):
        self.degree=degree ; self.xmax=xmax ; self.shift=shift
        if self.shift is None:
            self.shift=degree/2 # number of extra splines at each end
        # the splines are centered at -shift,-shift+1,...,ceil(xmax+shift)
        if x is not None:
            x=bigtools.float_array(x)
            x=bigtools.maddmirrored(x,self.shift) # uses MirrorOnBounds here        

            self.c=mfspline(x,degree,bcond=TBoundaryConvention['MirrorOnBounds'])
        else:
            self.c=c
        if self.c is None:
            if self.xmax is None:
                self.xmax=array((1.0,),float)
            self.c=zeros(bigtools.int_array(ceil(self.xmax))+1+2*self.shift,
                         float)
        if self.xmax is None:
            self.xmax=array(self.c.shape,float)-(2*self.shift+1.0)
        # flxmax=the floor of xmax, only used in evalint
        self.flxmax=floor(self.xmax).astype(int)
        self.dim=len(self.c.shape)

        if sometrue(self.xmax>array(self.c.shape)-1):
            raise "xmax is too small"

    def copy(self):
        """ Returns an independent copy of the signal """
        return MSplineSignal(c=array(self.c),xmax=self.xmax,
                             degree=self.degree,shift=self.shift)

    def getC(self):
        return self.c

    def setC(self,c):
        self.c=c

    def evalint(self,n=None):
        """ Evaluates signal at integers (0,1,..,n[0])x(0,1,...,n[1])x...
            n defaults to floor(xmax) """
        if n is None: n=self.flxmax
        x=mfirspline(self.c,self.degree,
                     bcond=TBoundaryConvention['MirrorOnBounds'])
        shifts=array((self.shift,)*self.dim,int)
        return x[bigtools.rangetoslice((shifts,shifts+n))]
        
        #-------------------------------------------------
                
    def bsplnevalfract(self, knot):
        """ Evaluates a B-spline of degree 'degree' at points
            -support+1/k,..,-1/k,0,1/k,..,support-1/k
            Returns a 1D float array 'kern' and the offset of the center point
            """
        bs=BIGsplines.Evalbspln(arange(0,(self.degree+1)/2.0,1.0/knot),self.degree)
        klen=bs.shape[0] # length of the half-kernel
        kern=zeros((2*klen-1),float) # make the full kernel
        kern[:klen-1]=bs[-1:0:-1]
        kern[klen-1:]=bs
        return kern,klen-1
        
    def evalfract(self,k=None,n=None):
        """ Evaluates the signal at the tensor product of
        0,1/k[i],2/k[i],3/k[i],...n[i].
        n defaults to xmax. n does not have to be an integer
        k and n must be vectors of size self.dim
        n should not be bigger than xmax
        """
        if k is None: k=1*self.dim
        k=bigtools.int_array(k)
        if n is None: n=self.xmax
        kernsofs=map(self.bsplnevalfract,list(k))
        x=array(self.c,'d')
        dims = len(x.shape)
        for dim in xrange(dims):
            arrayshape = list(x.shape)
            for i in xrange(arrayshape[1]):
                row = apply(BIGsplines.ConvolveUpsample, [x[:,i],kernsofs[dim][0],kernsofs[dim][1],k[dim]])
                if row.shape[0] != arrayshape[0]:
                    arrayshape[0] = row.shape[0]
                    y=zeros(arrayshape,'d')
                y[:,i] = row
            x = y.T
        shiftsl=array((self.shift,)*self.dim,int)*k
        shiftsh=floor(n*k+shiftsl).astype(int)
        return x[bigtools.rangetoslice((shiftsl,shiftsh))]
        
        #-------------------------------------------------

    def evalat(self,pts):
        """ Evaluates the signal at arbitrary points pts.
            pts should be of dimensionality dim+1 and its
            first dimension should be dim, so that pts(:,i) gives
            a coordinate of point i
            """
        pts=pts+self.shift # add offset
        return splineinterpol(self.c,pts,self.degree)

    def evalderat(self,pts,d):
        """ Evaluates the derivative of the signal with respect to
        the component d. Otherwise as evalat """ 
        pts=pts+self.shift # add offset 
        return splineinterpol(self.c,pts,self.degree,flag=4**d)
       

    def expand(self):
        """ Returns a twice-expanded signal, such that fnew(x/2)=fold(x).
            The expansion is therefore exact. Note that the number of
            added knots (shift) doubles."""
        lenc=self.c.shape[0]
        ce=bigpyramid.mbsexpand(self.c,self.degree,
                               bcond=TBoundaryConvention['MirrorOnBounds'])
        return MSplineSignal(c=ce,xmax=self.xmax*2.0,shift=2*self.shift,
                             degree=self.degree)

    def reduce(self):
        """ Returns a twice-reduced signal, optimal in the L2 sense.
        """
        nshift=(self.degree/2)*2 # minimum shift we want
        ashift=self.shift # actual shift we have
        nshift=max(((ashift+1)/2)*2,nshift) # new shift
        # WARNING: The following is suboptimal, the signal could be extended
        # asymmetrically
        if sometrue((array(self.c.shape)+1) % 2): # some dimension is even -> extend
            nshift+=1
        if ashift<nshift: # extend the signal using MirrorOnBoundary if needed
            c=bigtools.maddmirrored(self.c,nshift-ashift)
        else:
            c=self.c
        # now the shift is nshift and it is even
        c=bigpyramid.mbsreduce(c,self.degree,
                      bcond=TBoundaryConvention['MirrorOnBounds']) # reduce
        return MSplineSignal(c=c,xmax=self.xmax/2.0,shift=nshift/2,
                             degree=self.degree)

    def getDim(self):
        return self.dim

    def getShape(self):
        """ Returns the effective shape of the signal, i.e. what would
        be returned by evalint """
        return self.flxmax+1 

    def setXmax(self,x):
        """ Change xmax limit. No coefficients are modified.
        """
        if sometrue(x>array(self.c.shape)-1):
            raise "xmax is too small"
        self.xmax=x
        return self

    def addSignal(self,s,factor=1.0):
        """ Adds to myself an MSplineSignal s. My size is not changed,
            the signal s is either extended or shortened if needed.
            The signal s is optionally premultiplied by a multiplicative
            factor 'factor'
            """
        l=zeros(self.dim,int) # boundaries for self.c
        h=bigtools.int_array(self.c.shape)-1
        sl=zeros(self.dim,int) # boundaries for s.c
        sh=bigtools.int_array(s.c.shape)-1
        if self.shift>s.shift:
            l+=self.shift-s.shift
        else:
            sl+=s.shift-self.shift
        for i in range(self.dim):
            hdif=self.c.shape[i]-self.shift-s.c.shape[i]+s.shift
            if hdif>0: h[i]-=hdif
            else:      sh[i]+=hdif
        if factor!=1.0:  msc=factor*s.c
        else:            msc=s.c
        self.c[bigtools.rangetoslice((l,h))]+=msc[bigtools.rangetoslice((sl,sh))]
        return self

    def getContrib(self,x):
        """ Returns an array of the size of self.c which contains
        the spline values of the corresponding spline functions at point x
        """
        # evaluate B-spline kernels for all dims
        bvals=map(lambda s,x,shift=self.shift,d=self.degree:
          BIGsplines.Evalbspln(arange(-x-shift,-x+s-shift),d),
                  list(self.c.shape),list(x))
        return bigtools.tensorprod(bvals)

        
def test_MSplineSignal():
    x=reshape(arange(20),(4,5)) ; print "x=",x
    s=MSplineSignal(x=x)
    y=s.evalint(); print "y=",y
    z=s.evalfract(k=(2,2)) ; print "z=",z
    w=s.evalat(indices((4,5))/2.0) ; print "w=",w
    se=s.expand() ;
    print "expanded= ", se.evalint()
    sr=s.reduce() ; 
    print "reduced= ", sr.evalint()
    sre=sr.expand()
    #sre=SplineSignal(arange(10)).expand().expand().expand().reduce().reduce().reduce() 
    print "reduced/expanded= ", sre.evalint()
    ser=se.reduce() 
    print "expanded/reduced= ", ser.evalint()

def test_MSlena():
    import Image
    ima=bigtools.ImageToArray(Image.open('lena.tiff'))
    s=bigtools.timeop(lambda ima=ima: MSplineSignal(ima,degree=1), "Construct")
    x=bigtools.timeop(lambda s=s:s.evalint(),"Evaluate")
    print x.shape
    v0=bigtools.view(x)
    raw_input('Press any key') ; return
    s1=bigtools.timeop(lambda s=s: s.reduce(),"Reduce") 
    x=bigtools.timeop(lambda s1=s:s1.evalint(),"Evaluate")
    print x.shape ; v1=bigtools.view(x)
    s2=s1.reduce() ; x=s2.evalint(); print x.shape ; v2=bigtools.view(x)
    s3=s2.reduce() ; x=s3.evalint(); print x.shape ; v3=bigtools.view(x)
    imre=s3.expand().expand().expand().evalint()
    dif=abs(imre-ima)
    print "dif=",bigtools.maxelement(dif)
    v4=bigtools.view(dif,title='dif')
    imer=s.expand().reduce().evalint()
    dif=abs(imer-ima)
    print "dif=",bigtools.maxelement(dif)
    raw_input('Press any key')
    
def test_getContrib():
    s=MSplineSignal(xmax=(3,2))
    c=s.getC() ; c[1,2]=1 ; s.setC(c)
    print s.evalint()
    print s.getContrib((1,0))[1,2]

# ----------------------------------------------------------------------

class MSplineSignalList:
    """ A list of MSplineSignals, suitable for representing vector
        functions """

    def __init__(self):
        """ A primitive constructor. Makes an empty list """
        self.l=[]

    def zero(self,xmax,n,degree=3):
        """ Makes a MSplineSignalList containing
        n signals, capable of representing (multidimensional) interval
        0..xmax"""
        for i in xrange(n):
            self.l.append(MSplineSignal(xmax=xmax,
                                         degree=degree))
        return self

    def fromArray(self,c,n,xmax,degree=3):
        """ Makes a MSplineSignalList from
        an array c splitting it along the first dimension """
        for i in range(n):
            self.l.append(MSplineSignal(c=c[i],xmax=xmax,
                                         degree=degree))
        return self

    def copy(self):
        """ Returns an independent copy of the signal """
        o=MSplineSignalList()
        for i in self.l:
            o.l.append(i.copy())
        return o
                
    def toArray(self):
        """ Returns the list in the form of an array containing the
        coefficients c of the signals. """
        return array(map(lambda x: x.getC(),self.l))

    def evalfract(self,k=None,n=None):
        """ Applies an evalfract to all components, returns an array """

        # get the defaults to calculate the target size
        if k is None: k=1*self.l[0].dim
        k=bigtools.int_array(k)
        if n is None: n=self.l[0].xmax
        dim=len(self.l)
        r=zeros([dim,]+list(bigtools.int_array(n*k)+1),float)
        for i in range(dim):
            try:
                r[i]=self.l[i].evalfract(k=k,n=n)
            except: # Just for debugging, reallly
                print "n=",n," k=",k, "k*n=",k*n
                print "Exception occured: ",sys.exc_info()[:2]
                raise "Exception in evalfract"
        return r

    def evalat(self,pts):
        """ Applies evalat to all components, returns an array of size
        (dim,getShape). pts should be (dim,n) as for MSplineSignal.evalat """
        dim=len(self.l)
        r=zeros(pts.shape,float)
        for i in range(dim):
            r[i]=self.l[i].evalat(pts)
        return r

    def reduce(self):
        """ Applies reduce to all components. """
        self.l=map(lambda r: r.reduce(), self.l)
        return self

    def expand(self):
        """ Applies expand to all components. """
        self.l=map(lambda r: r.expand(), self.l)
        return self

    def multby(self,x):
        """ Multiplies all components by a factor of x """
        for i in self.l:
            i.c*=x
        return self

    def addSignal(self,s,factor=1.0):
        """ Adds to MS..List """
        for i in range(len(self.l)):
            self.l[i].addSignal(s.l[i],factor)
        return self

    def first(self):
        """ Returns the first component """
        return self.l[0]

    def setXmax(self,x):
        """ apply setXmax to all components """
        #print "setting xmax to", x
        for i in self.l:
            i.setXmax(x)
        return self
        
    def getContrib(self,x):
        """ call getContrib """
        return self.l[0].getContrib(x)

# ----------------------------------------------------------------------

def test_bigsplines():
    x=(2,5,-1)
    b=defaultbcond
    c=fspline(x,3,bcond=b)       # cubic spline coefficients
    print "x=",x,"c=",c
    # interpolate again
    p=range(len(x))
    p1=reshape(array(p),(1,3))
    y=splineinterpol(c,p1,3,bcond=b) 
    print "y=",y
    # now try the same thing in 2D
    c2=array((c,c,c))
    # print "c2=",c2
    p2=reshape(array((0.5*ones(len(p)),p)),(2,1,3))
    print "p2=",p2
    y2=splineinterpol(c2,p2,3,bcond=b)
    print "y2=",y2


def time_splineinterpol():
    r=bigtools.timeop(lambda : RandomArray.random((512,512)),'random')
    cr=mfspline(r,0) 
    tbl=indices(r.shape,float)
    y=bigtools.timeop(lambda cr=cr,tbl=tbl:splineinterpol(cr,tbl,0),
                      'splineinterp')
    print bigtools.maxelement(abs(r-y))
    
def test_splineinterpolone():
    c=zeros((6,3),'d')
    i=(1,0)
    c[i]=1.0
    deg=3
    tbl=indices(c.shape,'d')
    # print tbl, tbl.shape
    y1=splineinterpol(c,tbl,deg)
    y2=splineinterpolone(i,c.shape,tbl,deg)
    print y1
    print y2
    r=splinerange(i,c.shape,c.shape,zeros(len(c.shape)),
                      ones(len(c.shape)),deg)
    print r
    s=bigtools.rangetoslice(r)
    print y2[s]

    
def test_fir():
    x=(1,2,3,4,5,6,7,8,9,10)
    b=TBoundaryConvention['MirrorOnBounds']
    #c=array((0,0,0,0,0,1,0,0,0,0,0,0))
    print "x=",x
    #kernel=array((1,4,1))/6.0
    #print "c=",c,"kernel=",kernel
    # y=BIGsplines.FirConvolve(c,kernel,1)
    for i in range(8):
        c=fspline(x,i,bcond=b)
        y=firspline(c,i,bcond=b)
        print "y=",y

def test_evalfract():
    s=MSplineSignalList().zero((4,4,4),n=3)
    g=s.evalfract(k=(10,128,128),n=(39.0/10.0,511.0/128.0,511.0/128.0))
    print "Deformation ",g.shape
    s=MSplineSignal(xmax=(40,512,512))
    w=s.evalat(g)
    print "Warped ",w.shape

if __name__=='__main__': # running interactively
    # test_bigsplines()
    # test_fir() 
    test_mfspline()
    
