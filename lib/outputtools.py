from os import path
from os import makedirs

class PictureNumberNamer:

	def __init__(self, folder, format):
		self.string = path.join(folder,format)
	
	def generatename(self, image1, image2):
		return self.string % (image1.picturenumber, image2.picturenumber)
	
class CheckExistence:
		
	def checkExistence(self, dffname):
		"""
			XXX: this is used to check if results exist. 
			Why it tries to create folders?
		"""
		if not path.exists(path.dirname(dffname)):
			makedirs(path.dirname(dffname))
		elif path.exists(dffname):
			return True
		return False
