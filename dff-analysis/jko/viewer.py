

import wx

frame_width = 1000
frame_height = 700
frame_x = 100
frame_y = 0

window_top_height = 500
window_top_width = frame_width
window_item_spacing_vertical = 10
window_item_spacing_horizontal = 10
window_textbox_width = 200
window_textbox_height = 20
window_column_width = 500
window_label_width = 200
window_panel_width = 400
window_panel_height = 200
window_image_width = window_panel_width
window_image_height = window_panel_height

window_textbox_value = "bitmapProducer.py"

class Positioner:
    
    def createNewPlace(self, parent, compDict):
        """
            finds a place for itself. Reads positions of other objects in the same column
            and puts itself to the bottom.
        """
        # initial spacing to the top
        yPos = window_item_spacing_vertical
        
        # loop through components
        for key in compDict.keys():
            cItem = compDict[key]
            # if componen was in wrong column => skip it
            if not (self.col == cItem.col): continue
            # get the bottom location of the component
            cYPos = cItem.GetRect().GetBottom()
            # check if it was the lowest
            if yPos < cYPos:
                yPos = cYPos
        # add default spacing
        yPos += window_item_spacing_vertical
        
        # x coordinate is the default spacing + column number times column width
        x = window_column_width * self.col + window_item_spacing_horizontal
        y = yPos
        return (x,y)
    

class JFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 
                          pos = (frame_x, frame_y), 
                          size = (frame_width, frame_height))
        
        self.splitter = wx.SplitterWindow(self)
        
        self.bWindow = BottomWindow(self.splitter)
        self.tWindow = TopWindow(self.splitter, self.bWindow)
        self.splitter.SplitHorizontally(self.tWindow, self.bWindow, window_top_height)
        
class BottomWindow(wx.Window):
    
    def __init__(self, parent):
        wx.Window.__init__(self,parent, -1)
        self.compDict = {}
        DictTextCtrl(self, -1, "filename NW", col = 0, value = "bitmapProducerNW.py")
        DictTextCtrl(self, -1, "filename NE", col = 0, value = "bitmapProducerNE.py")
        DictTextCtrl(self, -1, "filename SW", col = 0, value = "bitmapProducerSW.py")
        DictTextCtrl(self, -1, "filename SE", col = 0, value = "bitmapProducerSE.py")
        DictTextCtrl(self, -1, "imageFolder", col = 1)
        DictTextCtrl(self, -1, "dffFolder", col = 1)
        DictTextCtrl(self, -1, "pictureNumber", col = 1)

class DictTextCtrl(wx.TextCtrl, Positioner):
    
    def __init__(self, parent, id, name, col = 0, value = window_textbox_value):
        # store defaults
        self.name = name
        self.parent = parent
        self.col = col
        
        # crete position
        pos = self.createNewPlace(parent, parent.compDict)
        size = (window_textbox_width, window_textbox_height)
        # create label
        self.label = wx.StaticText(parent, -1, self.name, pos)
        # create textbox position
        tcX = pos[0] + window_label_width + window_item_spacing_horizontal
        tcPos = (tcX, pos[1]) 
        # create textbox
        wx.TextCtrl.__init__(self, 
                             parent,
                             -1,
                             pos = tcPos,
                             size = size,
                             value = value)
        # add yourself to the list
        parent.compDict[name] = self
        
class ImagePanel(wx.Panel, Positioner):
    
    def __init__(self, parent, name, col = 0, bitmapProducerFn=None):
        
        self.parent = parent
        self.name = name
        self.col = col
        
        pos = self.createNewPlace(parent, parent.compDict)
        
        wx.Panel.__init__(self, parent, -1, pos = pos,
                 size = (window_panel_width, window_panel_height))
        self.parent.compDict[name] = self
        
        self.loadBitmap(bitmapProducerFn)
        
    def loadBitmap(self, bitmapProducerFn):
        
        if bitmapProducerFn == None: return
        print bitmapProducerFn
        execfile(bitmapProducerFn)
        image = bitmap
        image.SetSize((window_image_width, window_image_height))
        wx.StaticBitmap(self, -1, image, size = (window_image_width, window_image_height))
        
class TopWindow(wx.Window):
    
    def __init__(self, parent, bWindow): 
        wx.Window.__init__(self, parent, -1, size = (window_top_width, window_top_height))
        self.compDict = {}
        ImagePanel(self, "im NW", col = 0, bitmapProducerFn = bWindow.compDict["filename NW"].GetValue())
        ImagePanel(self, "im NE", col = 1, bitmapProducerFn = bWindow.compDict["filename NE"].GetValue())
        ImagePanel(self, "im SW", col = 0, bitmapProducerFn = bWindow.compDict["filename SW"].GetValue())
        ImagePanel(self, "im SE", col = 1, bitmapProducerFn = bWindow.compDict["filename SE"].GetValue())
        
#if __name__ == "__main__":
    
app = wx.App()
frame = JFrame() 
frame.Show()
app.MainLoop()