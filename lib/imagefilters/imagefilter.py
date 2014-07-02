
class ImageFilter:
    
    pass

class TrueFilter:
    
    def filter(self, image):
        return True

class ImageFilterFactory:
   
    def __init__(self):
    
        from picturenumberfilter import PictureNumberFilter
    
        self.imageFilterDictionary = dict({
                                           "true":TrueFilter,
                                           "picturenumber":PictureNumberFilter
                                           })
        
    def getImageFilters(self, configurationdict):
        filters = []
        for key, value in configurationdict.items():
            name = key.lower()
            filters.append(self.imageFilterDictionary[name](value))
        return filters
