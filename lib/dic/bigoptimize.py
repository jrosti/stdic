
""" Module bigoptimize implements multidimensional nonlinear optimization
    technique and some prototype problems

    Jan Kybic, October 2000
    $Id: bigoptimize.py,v 1.3 2006/08/07 13:24:59 jko Exp $
    """

import math
from numpy import *
import BIGsplines
import bigtools
import bigpyramid
import time
import bigsplines

# --------------------------------------------------------------------

class EvaluableProblem:
    """ Prototype multidimensional optimization problem

        E=(x0-1)^4+(x1-2)^4+(x2-3)^4+(x0-1)^2*(x1-2)^2*(x2-3)^2

        The minimum is clearly at (1,2,3)
    """

    def getInitialX(self): # returns a suitable first guess of the solution
        return array((0,0,0),Float) # just start with zeros

    def getE(self,x):      # return the scalar criterion to be minimized
        return (pow(x[0]-1,4)+pow(x[1]-2,4)+pow(x[2]-3,4)+pow(x[0]-1,2)*
                pow(x[1]-2,2)*pow(x[2]-3,2))

    def getEg(self,x):     # returns the criterion and its gradient
        return self.getE(x),array((
            4*pow(x[0]-1,3)+2*(x[0]-1)*pow(x[1]-2,2)*pow(x[2]-3,2),
            4*pow(x[1]-2,3)+2*(x[1]-2)*pow(x[0]-1,2)*pow(x[2]-3,2),
            4*pow(x[2]-3,3)+2*(x[2]-3)*pow(x[1]-2,2)*pow(x[0]-1,2)))

    def getEgDh(self,x):   # returns E,gr, and the diagonal of the Hessian
        r=self.getEg(x)
        return r[0],r[1],array((
            12*pow(x[0]-1,2)+2*pow(x[1]-2,2)*pow(x[2]-3,2),
            12*pow(x[1]-2,2)+2*pow(x[0]-1,2)*pow(x[2]-3,2),
            12*pow(x[2]-3,2)+2*pow(x[1]-2,2)*pow(x[0]-1,2)))

    # the following methods are ment mainly for testing

    def numg(self,x,h=1e-6): # calculate the gradient at x numericaly
        g=zeros(x.shape,Float) # here we store the gradient
        E=self.getE(x)
        for i in bigtools.getindices(x):
            xf=x+bigtools.basisv(x.shape,i)*h
            g[i]=self.getE(xf)-E # forward differencing
        return g/h
        

    def gerr(self,x,h=1e-6): # calculates the linf error of gradient computation
        return bigtools.maxelement(abs(self.getEg(x)[1]-self.numg(x,h)))

    def numDh(self,x,h=1e-6): # calculate the Hessian diagonal at x numericaly
        H=zeros(x.shape,Float) # here we store the gradient
        g=self.getEg(x)[1]
        for i in bigtools.getindices(x):
            xf=x+bigtools.basisv(x.shape,i)*h 
            H[i]=self.getEg(xf)[1][i]-g[i] # forward differencing
        return H/h

    def dHerr(self,x,h=1e-6): # calculates the linf error of Hessian computation
        return bigtools.maxelement(abs(self.getEgDh(x)[2]-self.numDh(x,h)))

    
# --------------------------------------------------------------------

class SimpleReducer:
      """ The SimpleReducer class assembles the expand and reduce operations
      based on linear averaging and linear interpolation. It works
      for matrices with arbitrary dimensions. """

      def simplereduce(self,x):
          """ reduce 1D vector by 3pt averaging """
          c=BIGsplines.FirConvolve(x,array((0.25,0.5,0.25)),1)
          return bigtools.downsample(c,2)

      def simpleexpand(self,x,targetlen=None):
          """ expand 1D vector by 3pt averaging """
          x=bigtools.upsample(bigtools.addmirrored(x,1),2)
          x=convolve(x,array((0.5,1,0.5)))
          xlen=x.shape[0]
          tlen=targetlen or xlen-2
          if tlen==xlen: return x
          if tlen==xlen-1: return x[:-1]
          if tlen==xlen-2: return x[1:-1]
          raise BIGsplines.error, 'Target length %d cannot be obtained' % tlen

      def reduce(self,x):
          """ reduce arbitrary vector/matrix x """
          #print "Simple reducing"
          # return bigpyramid.bsreduce(x,1)
          return bigsplines.applyseparablewithcopy(x,
                 lambda inp,s=self: s.simplereduce(inp) )

      def expand(self,x,targetlen=None):
          """ expand arbitrary vector x """
          #print "Simple expanding"
          # return bigpyramid.bsexpand(x,1)
          t=targetlen
          return bigsplines.applyseparablewithcopy(x,
                 lambda inp,s=self,tlen=None:
                 s.simpleexpand(inp,targetlen=tlen), targetlen=t )
          
# --------------------------------------------------------------------
class SamplingReducer(SimpleReducer):
      """ The SimpleReducer class assembles the expand and reduce operations
      based on sampling and linear interpolation. It works
      for matrices with arbitrary dimensions. """

      def simplereduce(self,x):
          """ reduce 1D vector by 3pt averaging """
          return bigtools.downsample(x,2)

      def simpleexpand(self,x,targetlen=None):
          """ expand 1D vector by 3pt averaging """
          x=bigtools.upsample(bigtools.addmirrored(x,1),2)
          x=convolve(x,array((0.5,1,0.5)))
          xlen=x.shape[0]
          tlen=targetlen or xlen-2
          if tlen==xlen: return x
          if tlen==xlen-1: return x[:-1]
          if tlen==xlen-2: return x[1:-1]
          raise BIGsplines.error, 'Target length %d cannot be obtained' % tlen
# --------------------------------------------------------------------


class SplineReducer(SimpleReducer):

    """ DOCUMENT """

    def getsplinedegree(self):
        deg=3
        try:
            deg=self.degc
            # print "getsplinedegree=",deg
        except:
            pass
        return deg

    def reduce(self,x):
        #print "Spline reducing"
        rx=bigpyramid.mbsreduce(x,self.getsplinedegree())
        return rx

    def expand(self,x,targetlen=None):
        #print "Spline expanding"
        y=bigpyramid.mbsexpand(x,self.getsplinedegree())
        if targetlen:
            targetlen=asarray(targetlen,Int)-1
            s=bigtools.rangetoslice((zeros(targetlen.shape),targetlen))
            y=y[s]
        return y

# --------------------------------------------------------------------

class OptimizerGdesP:
    """ Gradient descent optimizer for EvaluableProblem-like classes.
    Just go down along the gradient, adapting the step size as needed.

    It works almost exactly as bigoptimize.OptimizerGdes, except that
    parameters are given as a parameter object
    Usage:

    o=OptimizerGdesP(evaluableProblemInstance,parameters=None)
    while not o.hasConverged():
          o.makeStep()
    print o.getX()

    optional parameters include the starting point
    'startx', tolerances 'xtol', starting step 'startstep',
    step mult. factors 'stepf' and 'stepdownf', verbosity flag 'verbose'.
    
    Callback function 'cbf' can also be specified, which is then
    called whenever the criterion is evaluated.

    Some optimization has been performed to minimize the number
    of evaluations needed. 
    """

    def __init__(self,problem,par=None): # par are the Parameters
        self.p=problem
        self.par=bigtools.Parameters(par,
           default={ 'xtol':1e-3, 'verbose':0, 'minstep':1e-20,
                     'stepf': 9, 'stepdownf':10, 'startstep': 1.0 })
        self.i=0       # the iteration number (number of evaluations)
        self.x=None ; self.E=None ; self.dx=None ; self.gr=None
        self.step=self.par.startstep

    def hasConverged(self): # convergence criterion based on the change of x
        # maximum absolute change of x must be smaller than xtol
        if self.dx is None:
            return 0 # we have not yet tried
        if self.par.verbose>7:
            print "linf norm of dx=",bigtools.maxelement(abs(self.dx))
        return bigtools.maxelement(abs(self.dx))<=self.par.xtol

    def setX(self,x):
        self.x=x 
        self.E=None

    def getX(self):
        if self.x is None:
            if self.par.isdef('startx'):
                self.x=self.par.startx
            else:
                self.x=self.p.getInitialX() 
        return self.x

    def getEg(self):
        if self.E is None or self.gr is None:
            self.E,self.gr=self.p.getEg(self.getX())
            self.i+=1
        if self.par.isdef('cbf'):
            self.par.cbf(self.E,self.getX())
        return self.E, self.gr

    def getE(self):
        if self.E is None:
            self.E=self.p.getE(self.getX())
            self.i+=1
        if self.par.isdef('cbf'):
            self.par.cbf(self.E,self.getX())
        return self.E

    def makeStep(self):
        E,gr=self.getEg() # recover old ones if not known already
        self.dx=-gr*self.step
        if self.par.verbose>8:
                print "makeStep: i=%d step=%.3g dx=%.3g E=%.3g" % (self.i,
              self.step,bigtools.maxelement(abs(self.dx)),E)
        tx=self.x+self.dx
        tE,tgr=self.p.getEg(tx)
        self.i+=1
        if tE<=E: # successful step
            self.step*=self.par.stepf 
            self.x,self.E,self.gr=tx,tE,tgr
            self.success=1
            if self.par.verbose>5:
                print "Success: i=",self.i," step=",self.step," E=",self.E
        else:
            self.step=self.step/self.par.stepdownf # decrease step
            self.success=0
            if self.par.verbose>5:
                print "Failure: i=",self.i," step=",self.step," E=",tE
  
    def makeSuccessfulStep(self):
        # make steps until one is successful or until step-size drops
        # until a predefined threshold
        while 1:
            self.makeStep()
            if self.success or self.step<=self.par.minstep:
                return

    def getIterCount(self):
        return self.i

    def smoothToConvergence(self):
        """ Iterate until convergence is reached. By virtue of the
        stopping criterion, the last evaluation is always the best """
        while not self.hasConverged():
            self.makeStep()
        return self

# ----------------------------------------------------------------------

class OptimizerGdesQ(OptimizerGdesP):
    """ Adds automatic step-size calculation to OptimizerGdesP """
    def makeStep(self):
        E,gr=self.getEg() # recover old ones if not known already        
        self.dx=-gr*self.step
        if self.par.verbose>8:
                print "makeStep: i=%d step=%.3g dx=%.3g E=%.3g" % (self.i,
              self.step,bigtools.maxelement(abs(self.dx)),E)
        tx=self.x+self.dx
        tE,tgr=self.p.getEg(tx)
        self.i+=1
        if tE<=E: # successful step
            # Parabolic approximation
            try:
                candstep=0.5*(bigtools.sumall(self.dx*self.dx)/
                           (E-tE+bigtools.sumall(self.dx*tgr)))
            except ZeroDivisionError:
                print "division by zero calculating candstep"
                candstep=-1.0
            if candstep<=0.0:
                self.step*=self.par.stepf
            else:
                self.step=candstep
            self.x,self.E,self.gr=tx,tE,tgr            
            self.success=1
            if self.par.verbose>5:
                print "Success: i=%d step=%.3g dx=%.4g E=%.6g" % (self.i,
              self.step,bigtools.maxelement(abs(self.dx)),self.E)
        else:
            self.step=self.step/self.par.stepdownf # decrease step
            self.success=0
            if self.par.verbose>5:
                print "Failure: i=%d step=%.3g dx=%.4g E=%.6g" % (self.i,
              self.step,bigtools.maxelement(abs(self.dx)),tE)

# --------------------------------------------------------------------

class MROptimizerState:
    """ Encapsulates a state of a one level of a multiresolution optimizer.
    After instantiation, solveMR() is called to solve the problem.
    Then, the final state of the problem can be queried using
    getProblem(), or getOptimizer().

    New parameters include: optimizerClass (defaults to OptimizerGdesQ)
    and minlevel, minimum level at which we optimize (default is 0, optimize
    at all levels). If xtollast is set, it replaces xtol for level 0.
    maxlevel is the maximum level at which we descend.
    """

    def __init__(self,problem,par=None,level=0):
        """ Accepts an instance of an EvaluablemProblem problem,
        implementing the Multigridable protocol (functions canReduce(),
        getReduced(), and updateFine() )"""
        self.par=bigtools.Parameters(par,
               default={'optimizerClass': OptimizerGdesQ,
                        'minlevel':0, 'prcbf': None, 'xtollast':None,
                        'maxlevel':1000,'verbose':3 })
        self.p=problem
        # instantiate the optimizer
        if level==0 and self.par.xtollast is not None:
            paro=bigtools.Parameters(par,override={'xtol':self.par.xtollast})
        else:
            paro=self.par
        self.o=self.par.optimizerClass(self.p,paro)
        self.level=level
        if self.par.prcbf is not None:
            self.par.prcbf(self.p)

    def getProblem(self):
        return self.p

    def getOptimizer(self):
        return self.o

    def canReduce(self):
        return self.p.canReduce()

    def getReduced(self):
        """ Returns a reduced version of itself, passing the current
        optimization state along """
        rp=self.p.getReduced() # reduced problem
        # lower tolerance
        # NOTE: this assumes the absolute values of the solution
        # are also reduced
        # par=bigtools.Parameters(self.par,override={'xtol': self.par.xtol/2.0})
        return MROptimizerState(rp,self.par,level=self.level+1)

    def smoothToConvergence(self):
        """ Optimizes until convergence is reached.
            Returns a reference to self.
        """
        self.o.smoothToConvergence()
        return self

    def solveMR(self):
        """ Finds a solution to the problem using multiresolution approach.
        Returns a reference to self.
        """
        if self.par.verbose>3: time1=time.clock()
        if self.par.verbose>4:
            origE=self.o.getE()
        if self.level<self.par.maxlevel and self.canReduce():
            r=self.getReduced()           # get a reduced version of myself
            xc0=r.p.getXcopy()            # save the initial coarse level x
            
            r.solveMR()                   # solve at coarse level
            self.p.updateFine(xc0,r.p)    # update yourself
            self.o.setX(self.p.getInitialX()) # update optimizer state
        if self.par.verbose>4:
            befE=self.o.getE()
        if self.level>=self.par.minlevel:
            self.smoothToConvergence()
            # iterate at the fine level
        if self.par.verbose>4:
            print "solveMR at level %d E=%.3g > %.3g > %.3g " % (self.level,
                  origE,befE,self.o.getE())," iter: ",self.o.getIterCount()
        if self.par.verbose>3:
            print "solveMR at level ", self.level, " took ", \
                  time.clock()-time1, " s"
        return self

# --------------------------------------------------------------------

def test_evproblem(p,x=None,h=1e-6):
    import sys
    sys.float_output_precision=3
    #sys.float_output_suppress_small=1
    if not x: x=p.getInitialX()
    print "Criterion=",p.getE(x)
    print "Gradient analytic=",p.getEg(x)[1]
    print "Gradient numeric=",p.numg(x,h)
    print "Gradient evaluation error=", p.gerr(x,h)
    #print "Hessian analytic=",p.getEgDh(x)[2]
    #print "Hessian numeric=",p.numDh(x,h)
    #print "Hessian evaluation error=", p.dHerr(x,h)
