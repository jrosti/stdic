
from glob import glob

for fn in glob('*.tiff'):
    index = int(fn.split('-')[1])
    print 'mv %s pic-%04d-time_%d.tiff' % (fn, index,index)




