
    
    def plotIntegrals(self, outputfolder):
        
        for index in np.arange(1,len(self.dffs)+1):
            self.plotIntegral(index, outputfolder)
    
    def plotIntegral(self, linenumber=0, outputfolder=None):
        
        dff = self.dffs[linenumber-1]
        dffname = path.basename(dff).split('.')[0]
        dffreader = DffReader(dff)
        # Creation of y-directional strain rates.
        
        diffY = dffreader.defY - dffreader.origY
        derY = np.diff(diffY, 1, 0)
            
        skip = 16
            
        intervaly = [0,self.shape[0]]
        intervalx = [0,self.shape[1]]
        
        # Smoothing spline with length of cratesize.
        data = spline_filter(derY, skip)
        
        # Call the integrating function.
        integrals = self._integrateEs(data, skip, intervaly, intervalx)
        
        y,x = np.unravel_index(np.argmax(integrals), integrals.shape)
        y = skip*y
        x = skip*x
            
        print "Integral maximum at x=%d y=%d." % (x, y)
        
        # Plot of derY without spline filter.
        mpl.figure()
        mpl.contourf(derY,20)
        mpl.gca().invert_yaxis()
        
        # Plot of derY with spline filter.
        mpl.figure()
        mpl.contourf(data,20)
        mpl.gca().invert_yaxis()
        
        if outputfolder != None:
            mpl.savefig(path.join(outputfolder,"%s-splineEyy.png"))
        
        grid = np.mgrid[0:self.shape[0]:skip,0:self.shape[1]:skip]
        fig = mpl.figure()
        ax = Axes3D(fig)
        # 3D plot of integral values.
        ax.plot_surface(grid[0],grid[1], integrals, rstride=1, cstride=1)
        
        if outputfolder != None:
            mpl.savefig(path.join(outputfolder,"%s-integral.png"))
            
        
    def show(self):
        mpl.show()
        
    #--------------------------------------------------
    
    
    def plotIntegrals(self, outputfolder):
        
        for index in np.arange(1,len(self.dffs)+1):
            self.plotIntegral(index, outputfolder)
    
    def plotIntegral(self, linenumber=0, outputfolder=None):
        
        dff = self.dffs[linenumber-1]
        dffname = path.basename(dff).split('.')[0]
        dffreader = DffReader(dff)
        # Creation of y-directional strain rates.
        
        diffY = dffreader.defY - dffreader.origY
        derY = np.diff(diffY, 1, 0)
            
        skip = 16
            
        intervaly = [0,self.shape[0]]
        intervalx = [0,self.shape[1]]
        
        # Smoothing spline with length of cratesize.
        data = spline_filter(derY, skip)
        
        # Call the integrating function.
        integrals = self._integrateEs(data, skip, intervaly, intervalx)
        
        y,x = np.unravel_index(np.argmax(integrals), integrals.shape)
        y = skip*y
        x = skip*x
            
        print "Integral maximum at x=%d y=%d." % (x, y)
        
        # Plot of derY without spline filter.
        mpl.figure()
        mpl.contourf(derY,20)
        mpl.gca().invert_yaxis()
        
        # Plot of derY with spline filter.
        mpl.figure()
        mpl.contourf(data,20)
        mpl.gca().invert_yaxis()
        
        if outputfolder != None:
            mpl.savefig(path.join(outputfolder,"%s-splineEyy.png" % dffname))
        
        grid = np.mgrid[0:self.shape[0]:skip,0:self.shape[1]:skip]
        fig = mpl.figure()
        ax = Axes3D(fig)
        # 3D plot of integral values.
        ax.plot_surface(grid[0],grid[1], integrals, rstride=1, cstride=1)
        
        if outputfolder != None:
            mpl.savefig(path.join(outputfolder,"%s-integral.png" % dffname))
    
    def plotSmallIntegrals(self, linenumber=0, outputfolder=None):
        
        dffreader = DffReader(self.dffs[linenumber-1])
        y,x = self.points[linenumber - 1]
        
        # Creation of y-directional strainrates.
        
        diffY = dffreader.defY - dffreader.origY
        derY = np.diff(diffY, 1, 0)
            
        skip = 16
        oldskip = 32
            
        intervaly = [y-oldskip,y+oldskip]
        intervalx = [x-oldskip,x+oldskip]
        
        # Smoothing spline with length of cratesize.
        data = spline_filter(derY, skip)
        
        # Call the integrating function.
        integrals = self._integrateEs(data, skip, intervaly, intervalx)
        
        y,x = np.unravel_index(np.argmax(integrals), integrals.shape)
        y = skip*y
        x = skip*x
            
        print "Integral maximum at x=%d y=%d." % (x, y)
        
        rangey = np.r_[0:self.shape[0]:skip]
        rangex = np.r_[0:self.shape[1]:skip]
        
        booleany = (rangey >= intervaly[0])*(rangey <= intervaly[1])
        booleanx = (rangex >= intervalx[0])*(rangex <= intervalx[1])
        booleans = np.outer(booleany,booleanx)
                
        # Plot of derY without spline filter.
        
        derSmaller = derY[booleans]
        derSmaller = derSmaller.reshape(np.sqrt(derSmaller.shape[0]),-1)
        
        mpl.figure()
        mpl.contourf(derSmaller,20)
        mpl.gca().invert_yaxis()
        
        # Plot of derY with spline filter.
        
        dataSmaller = data[booleans]
        dataSmaller = dataSmaller.reshape(np.sqrt(dataSmaller.shape[0]),-1)
        
        mpl.figure()
        mpl.contourf(dataSmaller,20)
        mpl.gca().invert_yaxis()
        
        grid = np.mgrid[0:self.shape[0]:skip,0:self.shape[1]:skip]
        
        gridSmaller = grid[:,booleans]
        gridSmaller = gridSmaller.reshape(2,np.sqrt(gridSmaller.shape[0]),-1)
                
        integralsSmaller = integrals.copy()[booleans]
        integralsSmaller = integralsSmaller.reshape(np.sqrt(integralsSmaller.shape[0]),-1)
        
        print gridSmaller.shape
        print integralsSmaller.shape
        
        fig = mpl.figure()
        ax = Axes3D(fig)
        # 3D plot of integral values.
        ax.plot_surface(gridSmaller[0],gridSmaller[1], integralsSmaller, rstride=1, cstride=1)
