import sys
from os import path
import unittest
sys.path.append(path.join(path.dirname(sys.argv[0]), "test_transforms"))
import test_poly
import test_at
		
if __name__=="__main__":
	at_suite = unittest.defaultTestLoader.loadTestsFromModule(test_at)
	unittest.TextTestRunner().run(at_suite)
	poly_suite = unittest.defaultTestLoader.loadTestsFromModule(test_poly)
	unittest.TextTestRunner().run(poly_suite)
