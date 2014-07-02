
import unittest
import masterdata

class test_masterdata(unittest.TestCase):

	def testInitAndGetSet(self):
		configFn = "configFn"
		CALLER = "NAME"
		md = masterdata.MasterData()
		md.set("Caller", CALLER)
		self.assertEquals(md.get("Caller"), CALLER)
		self.assertTrue(md.check("Caller"))
