from dffreader import DffReader
import numpy as np
import sys
from imageclick.imageclickreader import ImageClickReader
from plots.plot import PlotFactory
from scipy.ndimage.interpolation import map_coordinates as mapc
import matplotlib.pyplot as mpl
from os.path import basename

def getPlot(plot, dff, x, y):
    
    dff = DffReader(dff)
    
    diffY = dff.defX - dff.origX
    eYY = np.diff(diffY, 1, 0)
    step = dff.step
    x = float(x)/step
    y = float(y)/step
    xcoords = np.r_[x:eYY.shape[1]:1]
    ycoords = y*np.ones_like(xcoords)
    coords = np.asarray([ycoords, xcoords], float)
    data = mapc(eYY, coords, output=float, order=3)
    
    plotfactory = PlotFactory()
    
    return plotfactory.getPlot(plot, data)

def createGenericPlot(length=100):
    
    x = np.r_[0:length]
    y = np.arctan(np.sqrt(1+np.power(x,2)))
    
    f = mpl.figure()
    mpl.plot(x,y, label="Generic arctan(sqrt(1+x^2)) plot")
    mpl.legend(loc=4)

if __name__=="__main__":
    
    imageclickfile = sys.argv[1]
    plot = sys.argv[2]
    
    ic = ImageClickReader(imageclickfile)
    try:
        index = int(sys.argv[3])
        dff = ic.dffs[index]
        x = ic.xs[index]
        y = ic.ys[index]
        plot = getPlot(plot, dff, x, y)
        plot.generatePlot("%s\nx=%d, y=%d" % (basename(dff),x,y))
        plot.show()
    except IndexError:
        createGenericPlot(50)
        mpl.show()