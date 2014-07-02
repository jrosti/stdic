
###############################################
# Runs sequence registers on test folders and
# checks outputs.
###############################################

import subprocess
import time
import os
from glob import glob
import sys



print "sequencetest/sequenceTest.py"
verbose = 1
registerCmd = 'python ../../register.py'
testFolder = 'testFolder'
outputBase = '/tmp/'

configBase = {    'sequence.name'        : '"Linear"',
        'dic.xtol'        : '0.1',
        'dic.degf'        : '3',
        'dic.degc'        : '3',
        'dic.verbose'        : '0',
        'dic.crate'        : '(16,16)',
        'order.name'        : '"PictureNumber"',
        'pairiterator.name'    : '"First"',
        'imageformat'        : '<<ignore>-<picturenumber>-time_<time>.tiff>',
        'overwrite'        : '"False"',
        'output.format'        : '"dff-%s-%s.dff"',
        'output.name'        : '"DffExporter"',
        'output.step'        : '10'}

def makeConfigFile(confDict, fn):

    outFile = open(fn,'w')
    for key in confDict.keys():
         outFile.write("%s = %s\n" % (key, confDict[key]))
    outFile.close()

def makeDefaultTest(    confDict, 
            correctList,
            outputBase,
            testFolder):
    outputDir = "%s/stdicTest_%lf" % (outputBase, time.time())
    os.mkdir(outputDir)
    configFn = outputDir + '/register.conf'
    makeConfigFile(confDict, configFn)

    cmd = registerCmd + ' ' + testFolder + ' ' + outputDir + '/dff ' + configFn
    cmd += "> /dev/null"
    subprocess.call(cmd, shell = True)

    currentList = glob(outputDir + '/dff/*')

    fCount = 0
    for fn in correctList:
        if not currentList.__contains__(outputDir + '/dff/' + fn):
            print "sequencetest/run_sequencetest.py failed" 
            raise ValueError()
        else:
            fCount +=1
    if verbose > 1:
        print 'Test Completed: %d/%d correct filenames' % (fCount, len(correctList)) 
    elif verbose > 0:
        print '.',
        sys.stdout.flush()

##############################################
# test 1
#
# linear start from first picture
##############################################

confDict = configBase

correctList1 = ['dff-0012-0029.dff', 'dff-0012-0046.dff', 'dff-0012-0021.dff', 'dff-0012-0015.dff', 'dff-0012-0020.dff', 'dff-0012-0030.dff', 'dff-0012-0016.dff', 'dff-0012-0017.dff', 'dff-0012-0023.dff', 'dff-0012-0042.dff', 'dff-0012-0014.dff', 'dff-0012-0044.dff', 'dff-0012-0022.dff', 'dff-0012-0039.dff', 'dff-0012-0026.dff', 'dff-0012-0041.dff', 'dff-0012-0013.dff', 'dff-0012-0035.dff', 'dff-0012-0019.dff', 'dff-0012-0032.dff', 'dff-0012-0037.dff', 'dff-0012-0038.dff', 'dff-0012-0027.dff', 'dff-0012-0018.dff', 'dff-0012-0034.dff', 'dff-0012-0033.dff', 'dff-0012-0031.dff', 'dff-0012-0043.dff', 'dff-0012-0024.dff', 'dff-0012-0047.dff', 'dff-0012-0045.dff', 'dff-0012-0048.dff', 'dff-0012-0036.dff', 'dff-0012-0028.dff', 'dff-0012-0049.dff', 'dff-0012-0025.dff', 'dff-0012-0040.dff']

# makeDefaultTest(confDict, correctList1, outputBase, testFolder)

##############################################
# test 2
#
# linear start from first picture
# picture skip = 10
##############################################

confDict = configBase.copy()
confDict['sequence.skip'] = '10'

correctList2 = ['dff-0012-0022.dff', 'dff-0012-0032.dff', 'dff-0012-0042.dff']

makeDefaultTest(confDict, correctList2, outputBase, testFolder)

##############################################
# test 3
#
# linear start from first picture
# picture skip = 10
# start = 2
##############################################

confDict = configBase.copy()
confDict['sequence.skip'] = '10'
confDict['sequence.start'] = '2'

correctList3 = ['dff-0014-0024.dff', 'dff-0014-0034.dff', 'dff-0014-0044.dff']

makeDefaultTest(confDict, correctList3, outputBase, testFolder)

##############################################
# test 4
#
# linear start from first picture
# picture skip = 10
# start = 2
# stop = 3
##############################################

confDict = configBase.copy()
confDict['sequence.skip'] = '10'
confDict['sequence.start'] = '2'
confDict['sequence.end'] = '3'

correctList4 = ['dff-0014-0024.dff', 'dff-0014-0034.dff']

makeDefaultTest(confDict, correctList4, outputBase, testFolder)

##############################################
# test 5
#
# linear start from next picture
# picture skip = 10
# start = 2
# stop = 3
# pairiterator.name = "Previous"
##############################################

confDict = configBase.copy()
confDict['sequence.skip'] = '10'
confDict['sequence.start'] = '2'
confDict['sequence.end'] = '3'
confDict['pairiterator.name'] = '"Previous"'

correctList5 = ['dff-0014-0024.dff', 'dff-0024-0034.dff']

makeDefaultTest(confDict, correctList5, outputBase, testFolder)


##############################################
# test 6
#
# linear start from next picture
# start = 2
# stop = 4
# pairiterator.name = "Previous"
##############################################

confDict = configBase.copy()
confDict['sequence.start'] = '2'
confDict['sequence.end'] = '5'
confDict['pairiterator.name'] = '"Previous"'

correctList5 = ['dff-0014-0015.dff', 'dff-0015-0016.dff']

makeDefaultTest(confDict, correctList5, outputBase, testFolder)

print " passed"


