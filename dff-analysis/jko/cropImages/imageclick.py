import gtk
import pygtk
import os

class ImageClick:

   
    def __init__(self,filename='default.tiff'):
        ''' Creates the window and listener using gtk.
        '''

        self.filename = filename
        
        self.x = None
        self.y = None
        self.x2 = None
        self.y2 = None

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.connect("destroy", self.destroy)
        self.window.connect("event", self.button_pressed)
        self.window.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.window.set_resizable(0)
        
        self.image = gtk.Image()
        self.image.set_from_file(self.filename)

        self.window.add(self.image)

        self.image.show()
        self.window.show()
        
        self.window.set_position(gtk.WIN_POS_CENTER)
        
        self.window.set_gravity(gtk.gdk.GRAVITY_NORTH_WEST)
        self.width, self.height = self.window.get_size()
        self.position = self.window.get_position()
        #self.window.move(-int(self.width/2),-int(self.height/2))
        #self.window.set_position(0)
        
        #self.window.set_position((-500,0))
        
    def destroy(self, widget, data=None):
        ''' Quits gtk
        '''
        self.window.destroy()
        self.image.destroy()
        gtk.main_quit()

    def button_pressed(self, widget, event):
        ''' Event handler assigned to listener. Reads and sets coordinates.
        '''
        
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            coords = event.get_coords()
            if self.x == None:
                self.x = int(round(coords[0]))
                self.y = int(round(coords[1]))
                ###################################

                ####################################
            else:
                self.x2 = int(round(coords[0]))
                self.y2 = int(round(coords[1]))
                ##########################################3   
                # self.printCommand()
                # self.destroy(self)
                ##########################################
                
                print self.filename, self.x, self.y, self.x2, self.y2
                self.destroy(self)
                
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            coords = event.get_coords()
            pos = self.window.get_position()
            x = -int(coords[0]) + 500 #-self.width
            y = -int(coords[1]) + 500 #-self.height
            self.window.move(x,y)
            #print pos, coords, x,y
            
                
    def printCommand(self):
        
        w = self.x2 - self.x
        h = self.y2 - self.y
        x0 = self.x
        y0 = self.y
        cmd = "mkdir -p cropped;"
        cmd += "for file in *.tiff; do "
        cmd += "convert -depth 8 -crop "
        cmd += str(w) + "x" + str(h)
        cmd += "+" + str(x0) + "+" + str(y0)
        cmd += " $file cropped/$file; done" 
        
        print cmd

    def main(self):
        ''' Starts gtk.main()
        '''
        gtk.main()
        
        
        
        