
""" Module bigtools provides various auxiliary functions for
    doing numerics and image processing with Python 

    It contains some utility routines, e.g. converting
    to/from PIL images, up/down sampling, ...


    Jan Kybic, October 2000
    $Id: bigtools.py,v 1.4 2006/10/04 05:35:38 jko Exp $

"""

"""

	Refactored and ported for numpy by Simo Tuomisto 2010

"""

from PIL import Image
from numpy import *
import time
import types
import bigsplines


# ----------------------------------------------------------------------

def ArrayToImage(a):
    """ converts array to greyscale or color image """
    if len(a.shape)==2:
        i=Image.fromstring('L',(a.shape[1],a.shape[0]),
                       (a.astype('B')).tostring())
    else: # color
        r,g,b=ArrayToImage(a[0]),ArrayToImage(a[1]),ArrayToImage(a[2])
        i=Image.merge("RGB",(r,g,b))
    return i    

def ImageToArray(iname):
    """ converts greyscale or color image to (byte) array """

    i = Image.open(iname)
    a=fromstring(i.tostring(),'B')
    a.shape=i.im.size[1], i.im.size[0]

    return a

def OpenedImageToArray(i):
    """ converts greyscale or color image to (byte) array """

    a=fromstring(i.tostring(),'B')
    a.shape=i.im.size[1], i.im.size[0]

    return a

def ImageToArrayWithCrop(iname, crop):
    """ converts greyscale or color image to (byte) array with crop """

    i = Image.open(iname)
    a=fromstring(i.tostring(),'B')
    a.shape=i.im.size[1], i.im.size[0]

    xstart = crop[0]
    xend = crop[1]
    ystart = crop[2]
    yend = crop[3]

    return a[ystart:yend, xstart:xend]

# ----------------------------------------------------------------------

def downsample(x,n):
    """ Downsample 1D array x by a factor of n, starting at the first
        element """
    return take(x,range(0,x.shape[0],n))

# ----------------------------------------------------------------------

def upsample(x,n):
    """ Upsample 1D array x by a factor of n, starting at the first
        element and filling gaps with zero. Returns a vector of length
        len(x)*n """
    y=zeros((x.shape[0],n),float)
    y[:,0]=x
    return y.ravel()

# --------------------------------------------------------------------

def mupsample(x,n):
    """ Upsample a multidimensional array x by a factor n[i] in
    direction i. Uses upsample. """
    
    return bigsplines.applyseparablewithcopy(x,
          lambda inp,n=n,ndim=None: upsample(inp,n[ndim]),passdim=1)

# --------------------------------------------------------------------

def mdownsample(x,n):
    """ Downsample a multidimensional array x by a factor n[i] in
    direction i. Uses downsample. """
    
    return bigsplines.applyseparablewithcopy(x,
          lambda inp,n=n,ndim=None: downsample(inp,n[ndim]),passdim=1)

# --------------------------------------------------------------------

def getindices(x=None,shape=None):
    """ Return a list of all indices of an array x. Usage:

    for i in getindices(x): # print all elements
        print x[i]
    """
    if not shape:
        shape=x.shape
    i=indices(shape)
    i=reshape(i,(i.shape[0],-1)) ; i=transpose(i)
    return i.tolist()

# --------------------------------------------------------------------

def basisv(shape,i, type=float):
    """ Return an  array of 'type' of shape 'shape', with all zeros except
        one at index i.
    """
    x=zeros(shape,type) ; x[i]=1.0
    return x

# --------------------------------------------------------------------

# for type comparisons such as type(points)!=ArrayType
ArrayType=type(array((1)))

# --------------------------------------------------------------------

def maxelement(x):
    """ Returns the value of the largest element of x, regardless of the
    dimensionality. """
    x=array(x)
    while type(x)==ArrayType and len(x.shape)>0:
        x=maximum.reduce(x)
    return x

# --------------------------------------------------------------------

def minelement(x):
    """ Returns the value of the smallest element of x, regardless of the
    dimensionality. """
    x=array(x)
    while type(x)==ArrayType and len(x.shape)>0:
        x=minimum.reduce(x)
    return x

# --------------------------------------------------------------------

def sumall(x):
    """ Returns the sum of all the elements of x, regardless of the
    dimensionality. """
    x=array(x)
    while type(x)==ArrayType and len(x.shape)>0:
        x=add.reduce(x)
    return x

# --------------------------------------------------------------------

def float_array(m):

    return asarray(m, float)

def int_array(m):
    """ Makes an int array out of m, accepting just about anything
    """
    
    try:
        return asarray(m, int)
    except TypeError:
        return m.astype(int) # round to int


# --------------------------------------------------------------------

def addmirrored(x,n):
    """ Take a 1D vector x and add n points at both ends, respecting the mirror
    on boundary conditions. """
    if n==0: return x
    x=float_array(x)
    y=zeros((x.shape[0]+2*n,),'d')
    y[0:n]=x[n:0:-1]
    y[n:n+x.shape[0]]=x
    y[-1:-n-1:-1]=x[-n-1:-1]
    return y

# --------------------------------------------------------------------

def maddmirrored(x,n):
    """ Apply addmirrored to a multidimensional x, extending
    it in all directions"""
    if n==0: return x
    return bigsplines.applyseparablewithcopy(x,
                            lambda inp,n=n: addmirrored(inp,n))

# --------------------------------------------------------------------

def rangetoslice(r):
    """ Given the range as returned by the splinerange
    in the form (array(l1,l2,l3,...),array(h1,h2,h3,...)),
    return a list of slice objects to be used for slicing """
    s=[]
    r=transpose(asarray(r,int))
    for i in range(len(r)):
        s.append(slice(r[i,0],r[i,1]+1))
    return s

# --------------------------------------------------------------------

def applyforallrows(x,oper,ndim=None):
    """ Apply an operation for all rows of x. The operation oper
    should take a 1D vector and return another 1D vector.

    If passdim is true, the 'oper' is passed a keyword argument
    'ndim' giving the dimension being processed.
    """
    xshape=x.shape ; dims=len(xshape)
    x=reshape(x,(-1,xshape[dims-1]))
    y=zeros(x.shape,float)
    for i in range(x.shape[0]): # for all 'rows'
        if ndim is None:
            y[i]=apply(oper,(x[i],)) # transform 'row'
        else:
            y[i]=apply(oper,(x[i],),{'ndim':ndim}) # transform 'row'
    x=reshape(x,xshape) # correct the shape of x
    return reshape(y,xshape)

# --------------------------------------------------------------------

def printtofile(img,filename,size=None,scale='auto',resample=Image.NEAREST):
    """ Save to a file a 2D array img, possibly scaled to 'size'
    which should be a tuple (xsize,ysize). The filename should
    already contain the extension. If no scaling is used (scale=None),
    the range is 0..255

    If img is 3D the first coordinate is assumed to be the color index,
    i.e. img[0] is red, img[1] green, and img[2] is blue

    resample defines the interpolation method, it can be NEAREST, BILINEAR,
    or BICUBIC, see Image.py
    """
    img=img.astype(float)
    if scale=='auto':
        maxel=maxelement(img)
        minel=minelement(img)
        scale=(minel,maxel)
    if scale:
        difel=scale[1]-scale[0]
        if difel==0: difel=1.0
        img=(img-scale[0])*255.0/difel
    img=choose(greater(img,255.0),(img,255.0))
    img=choose(greater(img,0.0),(0.0,img))
    pimg=ArrayToImage(img)
    if size:
        pimg=pimg.resize(size,resample=resample)
    pimg.save(filename)


# --------------------------------------------------------------------

def timeop(oper,comm='Operation'):
    t1=time.clock()
    r=apply(oper)
    t2=time.clock()
    print comm+' took %f s.' % (t2-t1)
    return r

# -------------------------------------------------------------------------


class Parameters:
    """ An object of class Parameters is a collection of parameters.
        Its instantiated as:

        p=Parameters(x)

        where x can be either another object of type Parameters,
        or a dictionary, such as

        p=Parameters({'tol':1e-6, 'startx':(0,0,0)})

        Additional keyword parameters to the constructor include:

        default: a dictionary with default values
        keep:    a list of parameter names to keep. If given, all other
                 parameters are discarded, except those given by
                 'default'
        discard: list of parameters to discard. This is done after
                 'default' and 'keep' are processed.
        override: these parameters are added as the last step

        Once the object is instantiated, the values can be read by
        as 'p.tol' or 'p.startx', they should not be changed this way
        (although this cannot be enforced for types passed by reference)
        For invalid names, KeyError is raised.

        Policy: parameter values should be never changed.
        
    """

    def __init__(self,p,default=None,keep=None,discard=[],override=None):
        self.p={}
        if default is not None:
            self.p.update(default)
        if p is not None:
            if type(p)==types.DictType:
                self.p.update(p)
            else:
                self.p.update(p.p) # p is a Parameters object
        if keep is not None:
            keep+=default.keys() # all keys we want to keep
            p={}
            for i in keep:
                p[i]=self.p[i] # copy what is needed
            self.p=p
        for i in discard:      # delete what we do not want
            del self.p[i]
        if override is not None:
            self.p.update(override)

    def isdef(self,name):
        """ Returns true if a parameter 'name' is defined """
        return self.p.has_key(name)

    def __getattr__(self,name):
        if self.isdef(name):
            return self.p[name]
        raise KeyError, "Unknown attribute: %s" % name

# -------------------------------------------------------------------------

def test_Parameters():
    p=Parameters({'a':0,'b':1,'c':"hmm"})
    print p.p, p.a, p.b, p.c
    q=Parameters(p,default={'a':100,'d':"d"})
    print q.p # should print a=0,b,c,d
    r=Parameters(p,default={'a':100,'d':"d"},keep=['b'])
    print r.p # should print a,b,d
    s=Parameters(r,discard=['a','d'])
    print s.p # should print b
