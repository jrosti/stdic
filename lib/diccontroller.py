from dic import *
import numpy as np

class DICController:

    def __init__(self, verbose=0, xtol=0.05, degf=3, degc=3, crate=(16,16), xstart=0, xend=-1, ystart=0, yend=-1):
        self.parameters = {"verbose": verbose, "xtol":xtol, 
                           "degf":degf, "degc":degc, 
                           "crate":crate}
        self.xstart = xstart
        self.ystart = ystart
        self.xend = xend
        self.yend = yend
        
    def analyze(self, image1, image2):
        
        imagearray1 = bigtools.OpenedImageToArray(image1)
        imagearray2 = bigtools.OpenedImageToArray(image2)
        
        if self.xend <= self.xstart:
            self.xend = imagearray1.shape[1]
        if self.yend <= self.ystart:
            self.yend = imagearray1.shape[0]
            
        imagearray1 = imagearray1[self.ystart:self.yend, self.xstart:self.xend]
        imagearray2 = imagearray2[self.ystart:self.yend, self.xstart:self.xend]
        
        par = bigtools.Parameters(self.parameters, override={'refimg':imagearray1,
                                                'testimg':imagearray2})
        warpingProblem = bigfelreg.MultigridableWarpingProblemBase(par=par)
        mrs = bigoptimize.MROptimizerState(warpingProblem, par=par)
        mrs.solveMR()
        self.deformationFunction = mrs.getProblem().datapart.testw
        self.shape = imagearray1.shape
        
    def getDeformationAtPoints(self, pointcollection):
        return self.deformationFunction.getDeformationAtPoints(np.array(pointcollection,float))
        
