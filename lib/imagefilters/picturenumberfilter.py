
from imagefilter import ImageFilter

class PictureNumberFilter(ImageFilter):
    
    def __init__(self, configdict):
        if 'analyzepicturenumber' in configdict:
            self.analyzepicturenumber = configdict['analyzepicturenumber']
        else:
            self.analyzepicturenumber = 1e100
        if 'firstpicturenumber' in configdict:
            self.firstpicturenumber = configdict['firstpicturenumber']
        else:
            self.firstpicturenumber = -1e100
        if 'lastpicturenumber' in configdict:
            self.lastpicturenumber = configdict['lastpicturenumber']
        else:
            self.lastpicturenumber = 1e100
        
    def filter(self, image):
        picturenumber = int(image.picturenumber)
        if (picturenumber == self.analyzepicturenumber):
            return True
        elif ((picturenumber >= self.firstpicturenumber) and (picturenumber <= self.lastpicturenumber)):
            return True
        else:
            return False
