
import os,sys
sys.path.append(os.path.abspath('../lib/'))

import unittest
from configparser import ConfigParser
#from masterdata import MasterData
from unittest import TestCase

import os
import inspect

class test_configparser(TestCase):
	
	def setUp(self):
		folder	= os.path.join("testsuite","test_masterdata")
		#self.configurationdata = MasterData()
		self.configparser = ConfigParser()
		fn = os.path.join(folder,"test_masterdata1.dicconf")
		self.configurationdata = self.configparser.parseFile(fn)

	def testIntegers(self):
		self.assertEquals(self.configurationdata.get("int"), 5)
		self.assertEquals(self.configurationdata.get("intWithWhitespace"), 32)
		self.assertEquals(self.configurationdata.get("intWithComment"), 7)

	def testFloats(self):
		self.assertAlmostEqual(self.configurationdata.get("float"), 3.14)
		self.assertAlmostEqual(self.configurationdata.get("floatWithWhitespace"), 42.11322)
		self.assertAlmostEqual(self.configurationdata.get("floatWithComment"), 11.27)

	def testTuples(self):
		self.assertEquals(self.configurationdata.get("tuple"), (3.14,1))
		self.assertEquals(self.configurationdata.get("tupleWithWhitespace"), (42.11322,32))
		self.assertEquals(self.configurationdata.get("tupleWithComment"), (11
																    ,27))
	def testStrings(self):
		self.assertEquals(self.configurationdata.get("string"), "3.14 = about pii")
		self.assertEquals(self.configurationdata.get("stringWithWhitespace"), "	whitespace   ")
		self.assertEquals(self.configurationdata.get("stringWithComment"), "stringtocomment")

	def testRegularExpressions(self):
		self.assertEquals(self.configurationdata.get("reg"), "(?P<3\.14>\w+)\.(?P<pii>\w+)\.txt")
		self.assertEquals(self.configurationdata.get("regWithWhitespace"),"(?P<		whitespace>\w+)")
		self.assertEquals(self.configurationdata.get("regWithComment"), "(?P<stringtocomment>\w+)")

	def testGetandSet(self):
		key = "number"
		value = 75.25
		self.configurationdata[key] = value
		self.assertAlmostEqual(self.configurationdata.get(key), 75.25)

if __name__ == "__main__":
    unittest.main()
   
