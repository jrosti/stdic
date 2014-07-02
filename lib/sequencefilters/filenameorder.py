from imageorder import ImageOrder
    
class FilenameOrder(ImageOrder):
    
    def __init__(self):
        ImageOrder.__init__(self)
        
    def _compare(self, image1, image2):
        
        if image1.filename < image2.filename:
            return -1
        elif image1.filename > image2.filename:
            return 1
        
        return 0
    
    def order(self, imagelist):
        return ImageOrder._order(self, imagelist, self._compare)
        