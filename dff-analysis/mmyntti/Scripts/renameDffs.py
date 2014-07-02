import sys
import os

# This script is meant for renaming .dff files in the way that they and
# folder crop_dff contain information about what sample the .dff belongs to.
# Takes also extra zeros away to make the result look nicer.

class rename:
	def __init__( self, filenames ):

		for fn in filenames:

			pathWithCropDff = fn.split("dff-000")[0]
			pathWithout = pathWithCropDff.split("/crop")[0]
			endPart = fn.split("/")[-1]
			sampleName = fn.split("/")[-3].split("_skip_")[0]

			newPath = pathWithout + "/crop_" + sampleName + "_dff/"
			newName = newPath + sampleName + "-" + endPart
			newName = newName.replace("000000", "") # Takes extra zeros away

			# Creates a new-named folder if there isn't one.
			if not os.path.exists(newPath):
				os.mkdir(newPath)

			os.rename(fn, newName)

			# Removes old folder if it's empty.
			if os.listdir(pathWithCropDff) == []:
				os.rmdir(pathWithCropDff)

			print "---"
			print fn 
			print " is changed to" 
			print newName

if __name__=="__main__":
    usage = "Usage :\t python renameDffs fileList"
	
    if len(sys.argv) < 1:
        print usage
        sys.exit()
        
    filenames = sys.argv[1:]
    runAnalysis = rename(filenames)
