

from glob import glob
import os
import numpy

#dffFolder = '/work/jko/angleCompression/IB7-1-R41-201106071247/cropped/dff/'
#dffFolder = '/work/jko/angleCompression/Matleenan_dfft/IB7-1-R41-201106071247_skip_9/crop_IB7-1-R41-201106071247_dff'
#dffFolder = '/work/jko/DIC-predict/emma/09021604/dff'
dffFolder = '~/Desktop/experiment_16/dff'

jpgFolder = dffFolder + '/../jpg' 

try:
    os.makedirs(jpgFolder)
except OSError:
    pass

for fn in glob(dffFolder + '/*.dff'):
    fn = os.path.basename(fn)
    print 'python plotdff.py %s/%s %s/%s.png %s/%s.dat' % (dffFolder, fn, jpgFolder,fn, jpgFolder, fn) 

######################################
# jarin correct strain
######################################

#from CorrectStrain import *
#saveArray = []
#for fn in glob(dffFolder + '/*.dff'):
#    (time, z)  = readydata(fn)
#    strainmat = relstrain(z)
#    (averaged, var, skewn, fluc, moment3) = computefluc(strainmat)
#    saveArray.append([time, averaged, var, skewn, fluc, moment3])
#sa = numpy.array(saveArray)
#numpy.savetxt(dffFolder + '/../t_mean_var_skew_std_third.dat', sa)
    
    
    
    
    
