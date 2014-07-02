import glob, trace, unittest, sys

""" Runs all tests """

if __name__=="__main__":
	modules = map(trace.fullmodname, glob.glob('test_*.py'))
	suite = unittest.TestLoader().loadTestsFromNames(modules)
	unittest.TextTestRunner().run(suite)