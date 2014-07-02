
class SequenceFilter:
    
    def __init__(self, orderer):
        self.orderer = orderer

class SequenceFilterFactory:
    
    def __init__(self):
        from linearsequence import LinearSequence
        
        self.sequenceFilterDictionary = dict({
                                              "Linear":LinearSequence
                                              })

    def getSequenceFilter(self, name, order, configdict=dict()):
        
        return self.sequenceFilterDictionary[name](order, **configdict)