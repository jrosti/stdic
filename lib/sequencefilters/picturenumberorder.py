from imageorder import ImageOrder
    
class PictureNumberOrder(ImageOrder):
    """
        Contains _compare function for picture numbers. 
        Image.picturenumber is typecast to float before comparing.  
        
        Image.picturenumber is a string. 
        
        "Order" function calls _order defined in parent. 
    """
    
    def __init__(self):
        ImageOrder.__init__(self)
        
    def _compare(self, image1, image2):
        
        if float(image1.picturenumber) < float(image2.picturenumber):
            return -1
        elif float(image1.picturenumber) > float(image2.picturenumber):
            return 1
        
        return 0
    
    def order(self, imagelist):
        return ImageOrder._order(self, imagelist, self._compare)
        