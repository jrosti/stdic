
class ImageOrder:
    
    def __init__(self):
        pass
    
    def _order(self, list, cmp):
        return sorted(list, cmp=cmp)
    
class ImageOrderFactory:
    
    def __init__(self):
    
        from picturenumberorder import PictureNumberOrder
        from filenameorder import FilenameOrder
        
        self.imageOrderDictionary = dict({
                                          "picturenumber":PictureNumberOrder,
                                          "filename":FilenameOrder
                                          })
    
    def getImageOrder(self, name, configdict=dict()):
        
        name=name.lower()
        return self.imageOrderDictionary[name](**configdict)
    
    
