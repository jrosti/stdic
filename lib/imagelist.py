
from imageobject import ImageObject

class ImageList:
    
    def __init__(self, folderobject, seqFilter,  imgFilters, regExpression=None):
        unorderedList = self._getFilteredFolder(folderobject, 
                                                imgFilters, 
                                                regExpression)
        self.imagelist = seqFilter.filter(unorderedList)
        
    def _getFilteredFolder(self, folderobject, imgFilters, regExpression=None):
                
        imagelist = []
        for filename in folderobject:
            imageObject = ImageObject(filename, regExpression)
            appendBoolean = True
            for imageFilter in imgFilters:
                if not imageFilter.filter(imageObject):
                    appendBoolean = False
                    break
            if appendBoolean:
                imagelist.append(imageObject)
        return imagelist
            
    def next(self):
        return self.imageiterator.next()
    
    def __iter__(self):
        return iter(self.imagelist)
