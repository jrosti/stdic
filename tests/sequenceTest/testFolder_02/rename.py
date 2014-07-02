

from glob import glob

for fn in glob('*.tiff'):
    number = fn.split('-')[1]
    number = int(number) - 10
    fn2 = fn.split('-')[0] + '-%d-' % (number) + fn.split('-')[2]
    print "mv ", fn, fn2
