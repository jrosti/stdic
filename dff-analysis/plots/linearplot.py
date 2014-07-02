import plot
import matplotlib.pyplot as mpl
import numpy as np

class LinearPlot(plot.Plot):
    
    def __init__(self, data):
        plot.Plot.__init__(self, data)
        
    def generatePlot(self, label=""):
        mpl.figure()
        y = self.data
        x = np.arange(y.shape[0])
        if len(label) > 0:
            mpl.plot(x,y, label=label)
        else:
            mpl.plot(x,y)