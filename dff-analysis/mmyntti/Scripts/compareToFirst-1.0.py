import sys
sys.path.append('/home/mmyntti/stdic')
import register as stdic
import os
import shutil
from glob import glob
import numpy as np
import Image

class runCalc:

    	def __init__( self, expList , workDir, skip ):

            # First read expList
            experiments = self.readConf(expList)

            #Copy images up to maxImN
            for expname in experiments.keys():

		print expname

                expDir = experiments[expname]["expDir"]
                imgDir = workDir + "/" + expname + "_skip_%d" % skip
                cropDir = imgDir + "/" + "crop"
                dffDir = imgDir + "_dff"
                rotAngle = experiments[expname]["rotAngle"]
                maxImN = experiments[expname]["maxImN"]

                # Copy images
                if os.path.exists(imgDir):
                    print  "Dir %s already exists. Assuming that images have already been copied!" % imgDir
                else:
                    self.copyImgs(expDir,imgDir,maxImN,skip)


                # Crop and rotate
                if os.path.exists(cropDir):
                    print "Crop directory %s already exists. Assuming images are ready." % cropDir
                else:
                    coord=(experiments[expname]["x0"],
                           experiments[expname]["x1"],
                           experiments[expname]["y0"],
                           experiments[expname]["y1"])
                    self.cropDir(imgDir,cropDir,coord,rotAngle)


            # run DIC calculations on cropped images
            for expname in experiments.keys():
                expDir = experiments[expname]["expDir"]
                imgDir = workDir + "/" + expname + "_skip_%d/crop" % skip
                dffDir = imgDir + "_dff"
                
                if os.path.exists(dffDir):
                    print "dffDir %s exists, Skipping DIC!" % dffDir
                else:
                    os.mkdir(dffDir)
                    if os.path.exists(dffDir + ".dicconf"):
                        dicConf = dffDir + ".dicconf"
                    else:
                        dicConf = workDir + "/" + "default.dicconf"
                        print imgDir
                        print dffDir
                        print dicConf
                        runAnalysis = stdic.Register(imgDir,dffDir,dicConf)
                        runAnalysis.run()



        def readConf(self, expList):
            
            # First parse the list of experiments to process
            file = open(expList,'r')
            lines = file.readlines()
            file.close()
            experiments = dict()
            try:
                i = 0
                while i < len(lines):

                    if lines[i][0]=="#":
                        i=i+1
                        continue

                    if lines[i]=="\n":
                        i=i+1
                        continue

                    expDir  = lines[i].split(',')[0]
                    if expDir[-1] == "/":                    # In case of a trailing slash
                        expname = expDir[:-1].split('/')[-1]
                    else:
                        expname = expDir.split('/')[-1]
                        
                    rotAngle = int( lines[i].split(',')[1] ) # Notice int() here!
                    maxImN   = int( lines[i].split(',')[2] )
                    x0       = int( lines[i].split(',')[3] )
                    x1       = int( lines[i].split(',')[4] )
                    y0       = int( lines[i].split(',')[5] )
                    y1       = int( lines[i].split(',')[6] )

                    experiments[expname] = {"expDir":expDir,
                                            "rotAngle":rotAngle,
                                            "maxImN":maxImN,
                                            "x0":x0,
                                            "x1":x1,
                                            "y0":y0,
                                            "y1":y1}
                    
                    i = i+1
                    
            except ValueError:
                print "Bad expList %s" % expList
                sys.exit()

            return experiments


        def copyImgs(self, expDir, imgDir, maxImN, skip):

            os.mkdir(imgDir)
            files = glob(expDir + "/*.tiff")
            files.sort()
            
            # We skip "skip" images in between the ones we take, so
            # the indices are 0, skip+1, 2*(skip+1), 3*(skip+1),...
            M = maxImN / (skip+1)
            indices = [0]*(M+1)
            j = 0
            for i in np.arange(1, M+1, 1):
                j = j + (skip+1)
                indices[i] = j
                
            toCopy = [files[i] for i in indices]
            for fn in toCopy:
                shutil.copy(fn,imgDir)
            


        def cropDir(self, imgDir, cropDir, coords, rotAngle):

            os.mkdir(cropDir)

            x0 = coords[0]
            x1 = coords[1]
            y0 = coords[2]
            y1 = coords[3]
            # Just crop the images to one size

            files = glob(imgDir + "/*.tiff")
            files.sort()

            i = 0
            while i < len(files)-1:
                im = Image.open(files[i])
                crop = im.crop( (x0,y0,x1,y1) )
                if not rotAngle == 0:
                    crop = crop.rotate(rotAngle)
                savefn = files[i].split('/')[-1]
                savefn = cropDir + "/" + savefn + "-crop.tiff"
                crop.save(savefn)
                i = i + 1


if __name__=="__main__":

    usage = "Usage :\t python compareToFirst-1.0.py expList.txt workDir skip"
	
    if len(sys.argv) < 3:
        print usage
        sys.exit()

    expList = sys.argv[1]
    if not os.path.exists(expList):
        print "expList %s not found!" % expList
        print usage
        sys.exit()
        
    workDir = sys.argv[2]
    if workDir[-1] == "/":
        workDir = workDir[:-1]
    if not os.path.exists(workDir):
        print "workDir %s not found!" % workDir
        print usage
        sys.exit()
    
    skip = int(sys.argv[3])
    if not skip >= 0:
        print "Bad skip value %d!" % skip
        print usage
        sys.exit()
        
    runanalysis = runCalc( expList, workDir, skip )
