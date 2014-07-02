import re

class Formatter:
    """ abstract class for an formatter """

    def __makeNumber__(self, number):
        try:
            inumber = int(number)
            return inumber
        except ValueError:
            fnumber = float(number)
            return fnumber

class NumberFormatter(Formatter):
    """ formats match as either an integer or a float """
    def getValue(self, match):
        return self.__makeNumber__(match.group('number'))

class StringFormatter(Formatter):
    """ formats match as a string """
    def getValue(self, match):
        stringvalue = match.group('string')
        if stringvalue == 'True':
            return True
        elif stringvalue == 'False':
            return False
        else:
            return stringvalue
        
class TupleFormatter(Formatter):
    """ formats match as a tuple """
    def getValue(self, match):
        value1 = match.group('number1')
        value2 = match.group('number2')
        return (self.__makeNumber__(value1), self.__makeNumber__(value2))        
        
class RegExpressionFormatter(Formatter):
    """ formats match as string that can be compiled to a regular expression """
    def getValue(self, match):    
        return self.__formatReg__(match.group('reg'))

    def __formatReg__(self, regExpression):
        regExpression = regExpression.replace(".", "\.")
        regExpression = regExpression.replace("<ignore>", ".+")
        regExpression = regExpression.replace("<","(?P<")
        regExpression = regExpression.replace(">", ">\w+)")
        return regExpression

class FormatterFactory:
    """ based on an format match, this instantiates a formatter """
    def __init__(self):
        numberRegExp = re.compile('(?P<number>[0-9.]+)$')
        stringRegExp = re.compile('\"(?P<string>.+)\"$')
        tupleRegExp = re.compile('\(\s*(?P<number1>[0-9.]+)\s*,\s*(?P<number2>[0-9.]+)\s*\)$')
        regexpRegExp = re.compile('\<(?P<reg>.+)\>$')
        self.matchlist = [(numberRegExp, NumberFormatter()), (stringRegExp, StringFormatter()), (tupleRegExp, TupleFormatter()), (regexpRegExp, RegExpressionFormatter())]
        
    def getFormatted(self, value):
        for regularExpression, formatter in self.matchlist:
            match = regularExpression.match(value)
            if match != None:
                return formatter.getValue(match)
