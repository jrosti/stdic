import matplotlib.pyplot as mpl

class PlotFactory:
    
    def __init__(self):
        
        from linearplot import LinearPlot
        #from logplot import LogPlot
        #from d3plot import D3Plot
        
        self.plots = dict({
                               "linear":LinearPlot
                               #"log":LogPlot
                               })
    
    def getPlot(self, name, data):
        
        return self.plots[name](data)
    
class Plot:
    
    def __init__(self, data):
        # Data should be a numpy array
        self.data = data
        mpl.savefig.extension = ".eps"
        
    def generatePlot(self):
        pass
        
    def show(self):
        mpl.legend(loc=4)
        mpl.show()
        
    def save(self, name):
        mpl.savefig(name)