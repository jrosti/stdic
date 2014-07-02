from unittest import TestCase
from expressionfolder import ExpressionFolder
from os import path
from os import getcwd

class test_ExpressionFolder(TestCase):
    
    def test_ExpressionFolder(self):
        
        pathname = getcwd()
        
        test_ExpressionFolder1 = ExpressionFolder(pathname)
        test_ExpressionFolder2 = ExpressionFolder(pathname)
        test_ExpressionFolder3 = ExpressionFolder(pathname)
        
        test_expression1 = '^expressionfolder\.py$'
        test_expression2 = '^test_expressionfolder\.py$'
        test_expression3 = '^.*expressionfolder\.py$'
        
        test_ExpressionFolder1.findWithExpression(test_expression1)
        test_ExpressionFolder2.findWithExpression(test_expression2)
        test_ExpressionFolder3.findWithExpression(test_expression3)
        
        result1 = path.join(pathname, 'expressionfolder.py')
        result2 = path.join(pathname, 'test_expressionfolder.py')
        result3 = [result1, result2]
        
        self.assertEquals(test_ExpressionFolder1.filelist[0], result1)
        self.assertEquals(test_ExpressionFolder2.filelist[0], result2)
        self.assertTrue(set(test_ExpressionFolder3.filelist) == set(result3))
        
        test_ExpressionIterator = iter(test_ExpressionFolder3)
        self.assertEquals(test_ExpressionIterator.next(), result1)
        self.assertEquals(test_ExpressionIterator.next(), result2)
        