

class Exporter:
	""" abstract base class for deformation data exporters """
	
	def export(self):
		if not self.initialize():
			return False
		self.writeVersion()
		self.writeMetadata()
		self.writeDeformationData()
		return self.finalize()
		
class ExporterClassFactory:
	
    def __init__(self):
        from dffexporter import DffExporter
        
        self.exporterDictionary = dict({
                                      	"DffExporter":DffExporter
                                       })

    def getExporterClass(self, name):
        
        return self.exporterDictionary[name]
       
class ExporterParameters:

    def __init__(self, step=10, dicconfig=dict()):
        self.step = step
        self.dicconfig = dicconfig
        
        
        
        
        
        
        
        
        
        
        
        
        