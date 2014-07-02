
""" Module representing the next generation of
    Fast Elastic Registration Algorithm
    as described in the corresponding chapter of my thesis.

    When this works, I will remove the routines from other modules
    which have thus become superflous.

    Jan Kybic, April 2001
    $Id: bigfelreg.py,v 1.3 2006/08/07 13:24:59 jko Exp $
"""

import new,time,operator,types
from numpy import *
import bigsplines
import bigtools
import bigoptimize
import BIGsplines


# ----------------------------------------------------------------------

class WarpableImageS:
    """ contains n-dimensional image to be warped.

    Reimplementation of bigregister.WarpableImage using MSplineSignal

    The ratio between the image size and the control grid size
    is now constrained to be an integer 'crate' (actually a vector)
    The deformation is a list of MSplineSignals, 'defs', one element for
    each component . It coincides with 'imgs' at zero and goes 'crate'
    times slower.

    """

    def __init__(self,imgs,defs=None,par=None,c=None):
        """ imgs is supposed to be MSplineSignal or an array,
            defs is either None, or a MSplineSignalList
            If imgs is an array, we convert it.
            The deformation defaults to identity, or it can be given
            by the MSplineSignal defs or the matrix c
            """
        if type(imgs)==bigtools.ArrayType:
            self.dim=len(imgs.shape)
        else:
            self.dim=imgs.getDim()
        self.par=bigtools.Parameters(par,
                   default={'degf':3,'degc':3,
                            'crate': array((8,)*self.dim,int),
                            'verbose': 0,
                            'cacheidentity': 1})
        self.imgs=imgs
        if type(self.imgs)==bigtools.ArrayType:
            self.imgs=bigsplines.MSplineSignal(x=self.imgs,degree=self.par.degf)
        self.par.crate=asarray(self.par.crate,int) # make sure it is Int 

        self.defs=defs
        self.g=None # the deformation evaluated at all points
        self.w=None # the warped image (an array)
        self.identity=None
        self.xmax=bigtools.float_array(self.imgs.getShape()-1)/self.par.crate

        if c is not None:
            self.setCFromArray(c)
        else:
            self.defs=defs
        if self.defs is None:
            self.setIdentity()
        else:
            self.defs.setXmax(self.xmax)
        self.dim=self.imgs.getDim()


    def setG(self,g):
        """ DOCUMENT """
        self.g = g;
        
    def setW(self,w):
        """ DOCUMENT """
        self.w = w;

    def setIdentity(self):
        """ DOCUMENT """
        if len(self.par.crate)!=self.dim:
            raise ValueError, 'Crate should be a vector of length %d' % self.cdim
        self.defs=bigsplines.MSplineSignalList().zero(
            self.xmax,self.dim,degree=self.par.degc)
        self.g=None ; self.w=None

    def getCAsArray(self):
        """ Unpacks the coefficients of the deformation to an array """
        return self.defs.toArray()

    def setCFromArray(self,c):
        """ Sets the internal representation of a deformation from an
        array c """
        self.defs=bigsplines.MSplineSignalList().fromArray(
            c,self.imgs.getDim(),self.xmax,degree=self.par.degc)
        self.g=None ; self.w=None 

        
    def getImageS(self):
        """ Return pointer to imgs """
        return self.imgs

    def getDefS(self):
        """ Return pointer the defs  MSplineSignalList """
        return self.defs

    def setDefS(self,defs):
        """ Set a new defs, invalidating the deformation """
        self.w=None ; self.g=None ; self.defs=defs 
        return self

    def getDeformation(self):
        """ Get the deformation function at all points, caching the
            results.
            """
        if self.g is None:
            if self.defs is None:
                raise AttributeError, "deformation not initialized"
            if self.identity is None: # identity is now cached
                if self.par.verbose>7:
                    self.identity=bigtools.timeop(lambda self=self:
                                       indices(self.imgs.getShape(),float),
                                       "indices")
                else:
                    self.identity=indices(self.imgs.getShape(),float)
            # begin with identity
            if not self.par.cacheidentity:
                self.g=self.identity ; self.identity=None
            else:
                self.g=array(self.identity)
            if self.par.verbose>7:
                time1=time.clock()
            self.g+=self.defs.evalfract(k=self.par.crate)
            if self.par.verbose>7:
                print "evalfract in getDeformation took ",time.clock()-time1, " s"
            self.w=None
        return self.g

    def getDeformationAtPoints(self,pts):
        """ Gets target position of multiple points pts of size (n,dim),
            (which is the transpose of what interpoldef wants)
            It returns the diplacements in the same format (n,dim)"""
        if len(pts.shape)==1: # just one point?
            pts=reshape(pts,(1,-1))
        if pts.shape[1]!=self.dim:
            raise "Incorrect shape for pts, pts.shape[1] should be %d" %self.dim
        pts=bigtools.float_array(reshape(pts,(-1,self.dim)))
        ptsnorm=pts/self.par.crate # grid point coordinates
        # get the dimensions right
        ptsnorm=reshape(transpose(ptsnorm),[self.dim]+[-1]+[1]*(self.dim-1))
        r=reshape(self.defs.evalat(ptsnorm),(self.dim,-1))
        return transpose(r)+pts # add identity deformation

    def getContrib(self,x):
        """ Returns an array of the size of self.defs.l[0].c which contains
        the spline values of the corresponding spline functions at point x
        """
        return self.getDefS().getContrib(x/self.par.crate)

    def getWarped(self,g=None):
        """ Get the warped image as an array """
        if self.w is None or g is not None:
            if g is None: g=self.getDeformation()
            if self.par.verbose>7:
                self.w=bigtools.timeop(lambda self=self,g=g:
                     self.imgs.evalat(g),"evalat in getWarped")            
            else:
                self.w=self.imgs.evalat(g)
        return self.w

    def getDerivatives(self):
        """ get all first derivatives of the image 
        """
        imgs=self.imgs
        derw=zeros([self.dim]+list(imgs.getShape()),float) 
        if self.par.verbose>7:
                time1=time.clock()
        g=self.getDeformation()
        if self.par.verbose>7:
                time2=time.clock()
        for i in range(self.dim):
            derw[i]=imgs.evalderat(g,i)
        if self.par.verbose>7:
                print "evalder took ",time.clock()-time2, " s, ",\
                      "getDeform ",time2-time1, " s"
        return derw

    def cRateIsEven(self):
        """ True if all elements of crate are even """
        return bigtools.sumall(self.par.crate % 2)==0

    def getReducedImg(self):
        """ Returns an equivalent version of WarpableImageS with twice
        reduced image and correspondingly modified deformation structure """ 
        if not self.cRateIsEven():
            raise "Cannot reduce, crate is odd"
        rimgs=self.imgs.reduce()
        rdefs=self.getDefS().copy().multby(0.5)
        par=bigtools.Parameters(self.par, override={'crate':self.par.crate/2})
        return WarpableImageS(rimgs,par=par,defs=rdefs)

    def getReducedImgAndDef(self):
        """ Returns an equivalent version of WarpableImageS with twice
        reduced image and twice reduced deformation grid.
        crate stays constant """ 
        rimgs=self.imgs.reduce()
        rdefs=self.getDefS().copy().reduce().multby(0.5)
        # print "getReducedImgAndDef shape", rimgs.getShape()
        return WarpableImageS(rimgs,par=self.par,defs=rdefs)

    def getReducedDef(self):
        """ Returns an equivalent version of WarpableImageS with twice
        reduced deformation grid. crate is multiplied by two """ 
        rdefs=self.getDefS().copy().reduce()
        par=bigtools.Parameters(self.par, override={'crate':self.par.crate*2})
        return WarpableImageS(self.imgs,par=par,defs=rdefs)

    def getExpandedDef(self):
        """ Returns an equivalent version of WarpableImageS with twice
        expanded deformation grid. crate is divided by two """ 
        if not self.cRateIsEven():
            raise "Cannot expand, crate is odd"
        rdefs=self.getDefS().copy().expand()
        par=bigtools.Parameters(self.par, override={'crate':self.par.crate/2})
        return WarpableImageS(self.imgs,par=par,defs=rdefs)

    def getWarpedOther(self,img):
        """ Warp an image img
             with the same deformation as myself, expanding appropriately
        """
        scf=img.shape/self.imgs.getShape() # integer division
        if scf*self.imgs.getShape()!=array(img.shape,int):
            raise ValueError, "Scaling factor must be an integer."
        c=self.getCAsArray() ; c*=reshape(scf,(-1,)+self.dim*(1,))
        par=bigtools.Parameters(self.par,
                  override={'crate': array(self.par.crate*scf,int)})
        wi=WarpableImageS(img,par=par,c=c)
        return wi.getWarped()
                                                   


    def getWarpingIndex(self,c):
        """ Calculates the warping index (average geometric error) between
        the current deformation and the deformation given by c."""
        c0=self.getCAsArray()    # remember the actual values
        g0=self.getDeformation() # find deformation
        self.setCFromArray(c)    # new deformation
        g1=self.getDeformation()
        
        npix=bigtools.prodall(g0.shape)
        g0=(g0-g1)**2
        wi=math.sqrt(bigtools.sumall(g0)/npix)
            
        self.setCFromArray(c0)   # give back the old deformation
        return wi

    def getWarpingIndexDefS(self,defs,par):
        """ Calculates the warping index (average geometric error) between
        the current deformation and deformation given by defs and
        par (from which crate, degc are taken) """
        g0=self.getDeformation()
        wi=WarpableImageS(self.imgs,defs=defs,par=par)
        g1=wi.getDeformation()


        npix=bigtools.prodall(g0.shape)
        g0=(g0-g1)**2
            
        wi=math.sqrt(bigtools.sumall(g0)/npix)
        return wi

    def getWarpingIndexG(self,g0):
        """ Calculates the warping index (average geometric error) between
        the current deformation and deformation given by g
        """
        par=bigtools.Parameters(self.par,override=
              {'crate':g0.shape[1:]/self.imgs.getShape()*self.par.crate})
        wi=WarpableImageS(bigsplines.MSplineSignal(xmax=array(g0.shape[1:])-1),
                          defs=self.defs,par=par)
        g1=wi.getDeformation()

        npix=bigtools.prodall(g0.shape)
        g0=(g0-g1)**2
        
        wi=math.sqrt(bigtools.sumall(g0)/npix)
        return wi

    def setProjection(self,g0):
        """ Given a conforming deformation table g0, set coefficients
        of the deformation so that it is as close as possible (in the
        warping index sense) to g0 """
        p=DProjProblem(self,g0)
        #bigoptimize.test_evproblem(p)
        #print "windexbefore=",self.getWarpingIndexG(g0)
        o=bigoptimize.OptimizerGdesQ(p,par=bigtools.Parameters(self.par,
                       override={'xtol':1e-4}))
        o.smoothToConvergence()
        #print "windexafter=",self.getWarpingIndexG(g0)
   
# ----------------------------------------------------------------------

class WarpingProblemS(bigoptimize.EvaluableProblem):
    """ Implements the accelerated variant of the single-scale
    warping problem. Mostly compatible with bigregister.WarpingProblem

    Accepts two images: reference and test. Reference is an array,
    test is a MSplineSignal which will be embedded in
    ReducWarpableImageS.

    The criterion is SSD per pixel.

    Implements the interface of EvaluableProblem.

    """

    def __init__(self,refimg,testimg=None,testw=None,par=None):
        """ refimg is an array, testimg a MSplineSignal
            or an array. Alternatively, you can specify testw
            (a WarpableImageS) directly """
        self.refimg=refimg
        self.par=bigtools.Parameters(par,
                   default={'degf':3,'degc':3,'verbose':0})
        if testw is not None:
            self.testw=testw
        else:
            self.testw=WarpableImageS(testimg,par=par)
            
        self.npix=multiply.reduce(self.refimg.shape)
        
        self.dim=len(refimg.shape)
        
    def getInitialX(self):
        """ Return the initial state of the deformation.
        It is a private copy of the array, it will not change with time """        
        return self.testw.getCAsArray()

    def getX(self):
        """ Currently homonyme for getInitialX(). Returns the last value
        used for the calculation """
        return self.testw.getCAsArray()


    def setX(self,x):
        """ Sets the deformation parameters to x. This functions is
        automatically called whenever new calculation of E or g is needed."""
        self.testw.setCFromArray(x)


    def getE(self,c):
        """ Calculate the criterion for a particular c"""
        self.setX(c) # pass c to the WarpableImage object
        self.wt=self.testw.getWarped() # get warped test image

        self.difwtrefimg=self.wt-self.refimg

        #bigtools.printtofile(self.difwtrefimg, 'difkuva.tif')

        E=bigtools.sumall(self.difwtrefimg**2) # the data part
        E/=self.npix
        return E

    def getEg(self,c):
        """ Calculate the criterion and its gradient for some c """
        E=self.getE(c) # side effects!, many variables get changed
        derw=self.testw.getDerivatives()
        # multiply all directional derivatives at each pixel
        # by F', where F is the criterion function

        derwp=2.0*self.difwtrefimg[newaxis,:]*derw
        gr=zeros(c.shape,float)
        # the next step is to convolve each component of derwp by
        # the upsampled B-spline kernel
        # WARNING: This is dependent on the MSplineSignal implementation
        # evaluate B-spline kernels for all dims
        kernsofs=map(lambda kk,d=self.testw.par.degc:
                     bigsplines.bsplnevalfract(kk,d),list(self.testw.par.crate))
        # let us make the executive function
        def convsub(inp,ndim=None,kernsofs=kernsofs,
                    shift=self.testw.defs.l[0].shift,
                    num=self.testw.defs.l[0].c.shape,
                    rate=self.testw.par.crate):
            kernel=kernsofs[ndim][0] ; kernorig=kernsofs[ndim][1]
            y=BIGsplines.ConvolveSubsamp(inp,kernel,
                    num[ndim],-kernorig-shift*rate[ndim],rate[ndim])
            #print "convsub inp=",inp.shape," out=",y.shape, " rate=",rate,\
            #      " ndim=",ndim, " num=",num
            return y
        #time1=time.clock()
        for i in range(self.dim):
            gr[i]=bigsplines.applyseparablewithcopy(derwp[i],convsub,passdim=1)
        #print "evalfract in getEg took ",time.clock()-time1, " s"
        gr/=self.npix
        return E,gr

# ----------------------------------------------------------------------


class MultigridableWarpingProblemSDataPart(WarpingProblemS):
    """ Implements the multigridable version of WarpingProblemS.

    The added methods are canReduce(), getReduced(), updateFine()

    When reducing, we will alternatively coarsen the image and
    the deformation grid, or coarsen both at the same time (default).

    Remark: For the moment, we consider only uniform coarsening
    of the deformation grid

    It is not intended to be run independently. Instead it will be
    a part of a WarpingProblemS object, together with other parts
    of the criteria.
    """

    def __init__(self,par=None):
        """ The par members refimg and testimg
            are either an array or a MSplineSignal.
            Alternatively, you can specify testw
            (a WarpableImageS) directly """
        # add minimal image size threshold, flags, etc.
        self.par=bigtools.Parameters(par,
                   default={'minimgsize':16, 'degc':3,
                            'degf':3, 'alternatered':1,
                            'reducedimg':0,'reduceddef':0,
                            'refimg':None,'testimg':None,'testw':None})
        self.reducedimg=self.par.reducedimg # the flag to know what to do next
        self.reduceddef=self.par.reduceddef # and how to come back
        refimg=self.par.refimg ; testimg=self.par.testimg
        
        testw=self.par.testw

        if type(refimg)==bigtools.ArrayType:
            self.refimgs=bigsplines.MSplineSignal(x=refimg,degree=self.par.degf)
        
        else: # refimg is already a MSplineSignal
            self.refimgs=refimg
            refimg=self.refimgs.evalint() # get the image values

        # call parent
        WarpingProblemS.__init__(self,refimg,testimg=testimg,
                                 testw=testw,par=self.par)

        #print "bigfelreg, line 506"
        #print "refimg: ", refimg
        #print "testimg: ", testimg
        #print "testw: ", testw
        
   
        if self.par.verbose>3:
            print "MultigridableWarpingProblemS with \n  img size=",\
            self.refimg.shape, "\n  crate=",self.testw.par.crate, "\n  csize=",\
            self.testw.defs.first().c.shape, "\n" # , " xmax=",self.testw.xmax

    def canReduceImg(self):
        """ True if Img can be reduced """
        r1=bigtools.minelement(self.refimg.shape)>self.par.minimgsize
        r2=not self.testw.cRateIsEven()
        return r1 and (r2 or self.canReduceDef())

    def canReduceDef(self):
        """ Returns true if the deformation can be further coarsened """
        return bigtools.minelement(self.testw.getDefS().first().xmax)>1.0

    def canReduce(self):
        """ True if any coarsening is possible """
        if self.par.alternatered:
            return self.canReduceImg() or self.canReduceDef()
        else:
            return self.canReduceImg() and self.canReduceDef()

    def getReducedAlternate(self):
        """ Returns a reduced version of the MultigridableWarpingProblemS,
            alternatively reducing the image size and the deformation
            grid size.
        """
        if self.reducedimg: # time to reduce the deformation grid
            if self.canReduceDef():
                return self.getReducedDef()
            if self.canReduceImg():
                return self.getReducedImg()
        else: # reduce the image
            if self.canReduceImg():
                return self.getReducedImg()
            if self.canReduceDef():
                return self.getReducedDef()
        raise "This problem cannot be reduced any more"

    def getReduced(self):
        """ Returns a reduced version of the MultigridableWarpingProblemS
            the particular reducing method can be chosen by the parameters """

        if self.par.alternatered:
            return self.getReducedAlternate()
        
        else:
            return self.getReducedImgAndDef()

    def getReducedImgAndDef(self):
        """ Reduce both image and deformation grid """
        rimgs=self.refimgs.reduce()
        rtestw=self.testw.getReducedImgAndDef()
        par=bigtools.Parameters(self.par,
              override={'refimg':rimgs,
                        'testw':rtestw,'reducedimg':1,'reduceddef':1,
                        'crate':rtestw.par.crate})
        return self.__class__(par=par)
    
    def getReducedImg(self):
        """ Returns a reduced version of the MultigridableWarpingProblemS
            with reduced images and possibly also the deformation grid,
            if needed
        """
        rimgs=self.refimgs.reduce()
        if self.testw.cRateIsEven():
            rtestw=self.testw.getReducedImg()
        elif self.canReduceDef(): # try to reduce both
            rtestw=self.testw.getReducedImgAndDef()
        else:
            raise "The image in this problem cannot be reduced any more"
        par=bigtools.Parameters(self.par,
              override={'refimg':rimgs,
                        'testw':rtestw,'reducedimg':1,'reduceddef':0,
                        'crate':rtestw.par.crate})
        return self.__class__(par=par)


    def getReducedDef(self):
        """ Returns a reduced version of the MultigridableWarpingProblemS
            with reduced deformation grid.
        """
        rtestw=self.testw.getReducedDef()
        par=bigtools.Parameters(self.par,override={'refimg':self.refimgs,
                        'testw':rtestw,'reducedimg':0,'reduceddef':1,
                        'crate':rtestw.par.crate})
        return self.__class__(par=par)


    def getXcopy(self):
        """ Get a copy of the current state, to be used with updateFine() """
        return self.getXstate().copy()

    def getXstate(self):
        """ Get the current state (no copy), to be used with updateFine() """
        return self.testw.getDefS()

    def updateFine(self,xc0,cp):
        """ Update yourself from the result of coarse level computation.
        xc0 is the coarse grid value received from cp.getXcopy()
        (a private copy) before the coarse grid representation.
        It might or might not be an array.
        cp is the coarse level MultigridableWarpingProblemS in its
        final state. The new fine value is
        xforig+Expand(xc1-xc0) """
        # make a copy of the current coarse level deformation
        coarsedefs=cp.getXcopy()
        coarsedefs.addSignal(xc0,factor=-1.0) # calculates xc1-xc0

        if cp.par.reducedimg:
            # image size changed, we need to multiply
            #print "updateFine multiplying"
            coarsedefs.multby(2.0)

        #print self.getInitialX().shape, xcdif.shape

        if cp.par.reduceddef:
            # deformation grid size changed, we need to expand
            coarsedefs=coarsedefs.expand()
            #print "updateFine expanding xmax=",coarsedefs.first().xmax
            
        finedefs=self.getXstate()
        #print "updateFine finedefs xmax=",finedefs.first().xmax

        expdefs=finedefs.addSignal(coarsedefs)
        self.setXstate(expdefs)
        return self

    def setXstate(self,x):
        """ Converse of getXstate() or getXcopy() """
        self.testw.setDefS(x)
        return self

# ----------------------------------------------------------------------

class MultigridableWarpingProblemBase(bigoptimize.EvaluableProblem):
    """ This is the basis versions of a WarpingProblemS.
        Additional plug-in criteria parts can be added.

        The object of a created class supports the following
        interface methods:
        __init__(self,par=None)
        getInitialX,getE,getEg,setX
        canReduce,getReduced,getXstate,getXcopy,updateFine

        These interface methods must be supported by the first (DataPart)
        client object, the auxiliary ones only need to support

        getE,getEg,canReduce,getReduced

        The auxiliary criterion objects will get an additional keyword argument
        datapart for their __init__ and getReduced() methods and
        should access the current state
        through this pointer.

        The possible parameters object par attributes are refimg,
        testimg, testw, and many others
        
        """
    # a list of classes. 
    # It should be enough to change this tuple when plug-in criterion
    # classes are added
    datapartclass=MultigridableWarpingProblemSDataPart
    """ DOCUMENT """
    auxclasses=()
    """ DOCUMENT """

    def __init__(self,par=None):
        """ instantiate the first object """
        self.datapart=self.datapartclass(par=par)
        """ DOCUMENT """
        self.auxobjects=[ o(par=par,datapart=self.datapart)
                            for o in self.auxclasses ]
        """ DOCUMENT """

    def getInitialX(self):
        """ Gets the initial value of X. We only relay this call
        to the first (data part) member"""
        return self.datapart.getInitialX()

    def getX(self):
        """ Gets the value of X. We only relay this call
        to the first (data part) member"""
        return self.datapart.getX()

    def getE(self,x):
        """ Relay the call to all members and accumulate """
        r=[ self.datapart.getE(x)]+[ o.getE(x) for o in self.auxobjects ]
        return reduce(operator.add,r)

    def getEg(self,x):
        """ Relay the call to all members and accumulate """
        r=[self.datapart.getEg(x)]+[ o.getEg(x) for o in self.auxobjects ]
        return reduce(lambda x,y: (x[0]+y[0],x[1]+y[1]),r)

    def setX(self,x):
        """ Relay the call to the data part """
        self.datapart.setX(x)
        return self

    def setXstate(self,x):
        """ Relay the call to the data part """
        self.datapart.setXstate(x)
        return self

    def canReduce(self):
        """ Relay the call to all members and accumulate """
        r=[ self.datapart.canReduce()]+[ o.canReduce() for o in self.auxobjects ]
        return reduce(operator.and_,r) # bitwise and. Hopefully does not matter

    def getReduced(self):
        """ Returns an object of my own class, containing reduced
        versions of myself and the auxiliary criterion parts. """
        rdatapart=self.datapart.getReduced()
        rauxobjects=[o.getReduced(datapart=rdatapart) for o in self.auxobjects ]
        r=new.instance(self.__class__,{})
        r.datapart=rdatapart
        r.auxobjects=rauxobjects
        return r
    
    def getXstate(self):
        """ Relay the call to the data part """
        return self.datapart.getXstate()

    def getXcopy(self):
        """ Relay the call to the data part """
        return self.datapart.getXcopy()

    def updateFine(self,xc0,cp):
        """ Relay the call to the data part """
        self.datapart.updateFine(xc0,cp.datapart)
        return self

#----------------------------------------------------------------------

if __name__=='__main__': # running interactively
    test_MultigridableWarpingProblemS()
