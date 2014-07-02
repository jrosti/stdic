import glob, trace, unittest, sys, os

""" argv[1:] is globbing. runs tests matching to the glob (aka sh wildcards) """

if __name__=="__main__":
	for g in sys.argv[1:]:
		testFNs = glob.glob(g)
				
		# add folders to the path, nasty, but python 2.4 does not have decent packages
		map(lambda x: sys.path.append(os.path.dirname(x)), testFNs)
		
		modules = map(trace.fullmodname, testFNs)
		suite = unittest.TestLoader().loadTestsFromNames(modules)
		print "Running a test (globbing): " + g
		unittest.TextTestRunner().run(suite)
