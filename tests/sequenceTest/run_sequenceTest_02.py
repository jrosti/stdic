
###############################################
# Runs sequence registers on test folders and
# checks outputs.
###############################################

import subprocess
import time
import os
from glob import glob
import sys



print "sequencetest/sequenceTest_02.py"
verbose = 1
registerCmd = 'python ../../register.py'
testFolder = 'testFolder_02'
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

correctList1 = ['dff-2-19.dff', 'dff-2-36.dff', 'dff-2-11.dff', 
                'dff-2-5.dff', 'dff-2-10.dff', 'dff-2-20.dff',
                'dff-2-6.dff', 'dff-2-7.dff', 'dff-2-13.dff', 
                'dff-2-32.dff', 'dff-2-4.dff', 'dff-2-34.dff', 
                'dff-2-12.dff', 'dff-2-29.dff', 'dff-2-16.dff', 
                'dff-2-31.dff', 'dff-2-3.dff', 'dff-2-25.dff',
                'dff-2-9.dff', 'dff-2-22.dff', 'dff-2-27.dff', 
                'dff-2-28.dff', 'dff-2-17.dff', 'dff-2-8.dff', 
                'dff-2-24.dff', 'dff-2-23.dff', 'dff-2-21.dff', 
                'dff-2-33.dff', 'dff-2-14.dff', 'dff-2-37.dff', 
                'dff-2-35.dff', 'dff-2-38.dff', 'dff-2-26.dff',
                'dff-2-18.dff', 'dff-2-39.dff', 'dff-2-15.dff',
                'dff-2-30.dff']

makeDefaultTest(confDict, correctList1, outputBase, testFolder)

##############################################
# test 2
#
# linear start from first picture
# picture skip = 10
##############################################

confDict = configBase.copy()
confDict['sequence.skip'] = '10'

correctList2 = ['dff-2-12.dff', 'dff-2-22.dff', 'dff-2-32.dff']

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

correctList3 = ['dff-4-14.dff', 'dff-4-24.dff', 'dff-4-34.dff']

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

correctList4 = ['dff-4-14.dff', 'dff-4-24.dff']

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

correctList5 = ['dff-4-14.dff', 'dff-14-24.dff']

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

correctList5 = ['dff-4-5.dff', 'dff-5-6.dff']

makeDefaultTest(confDict, correctList5, outputBase, testFolder)

print " passed"


