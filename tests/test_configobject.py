
import sys, os
sys.path.append(os.path.abspath("../lib/"))

import unittest
from unittest import TestCase
from configparser import ConfigParser
#from configobject import *

class test_ConfigObject(TestCase):        
    
    """
        DEPRECATED
        This is a bit redundant. ConfigObject is now just a
        nested dictionary.
      
    
    def test_subs(self):
        
        root = ConfigObject('root')
        root.sub('sub1')
        root.sub('sub2')
        root.sub1.sub('sub11')
        root.sub2.sub('sub21')
        
        root.value = 1
        root.sub1.value = 2
        root.sub2.value = 3
        root.sub1.sub11.value = 4
        root.sub2.sub21.value = 5
        
        resultdict = {
                      'value': 1,
                      'sub1.value': 2,
                      'sub2.value': 3,
                      'sub1.sub11.value': 4,
                      'sub2.sub21.value': 5
                      }
        
        valuedict = root.getValues()
        
        for key, value in resultdict.iteritems():
            self.assertEquals(valuedict[key], value)
            
    def test_getSubs(self):
    
        root = ConfigObject('root')
        root.sub('sub1')
        root.sub('sub2')
        
        resultdict = dict({
                           'sub1':root.sub1,
                           'sub2':root.sub2
                           })
        
        subdict = root.getSubs()
        
        for key, value in resultdict.iteritems():
            self.assertEquals(subdict[key], value)
    """
        
class test_ConfigObjectParser(TestCase):        
    
    def test_parse(self):
        parser = ConfigParser()
        configobject = parser.parseFile('testsuite/test_configobject.conf')
        resultdict = {
                      'numbers' : {'int1'       : 1,
                                   'int2'       : 2,
                                   'float'      : 1.1,
                                   'pi'         : 3.14},
                      'strings' : {'string1'    : "string1",
                                   'string2'    : "string2"},
                      'tuples'  : {'tuple1'     : (1,2),
                                   'tuple2'     : (1,2.1)},
                      'regexps' : {'reg1'       : "*\\.txt",
                                   'reg2'       : "(?P<jotain>\\w+)-(?P<jotain>\\w+)\\.picture"},
                      'boolean' : {'true'       : True,
                                   'false'      : False}
                      }

        
        resultdict2 = {
                      'int1' : 1,
                      'int2' : 2,
                      'float' : 1.1,
                      'pi' : 3.14
                      }
        
        valuedict2 = configobject['numbers']
                
        countValues = 0 
        for hKey in resultdict.keys():
            for lKey in resultdict[hKey].keys(): 
                self.assertEquals(resultdict[hKey][lKey], 
                                  configobject[hKey][lKey])
                countValues += 1
        self.assertEqual(countValues, 12) 
        for key, value in resultdict2.iteritems():
            self.assertEquals(valuedict2[key], value)
            
            
if __name__ == "__main__":
    unittest.main()
    