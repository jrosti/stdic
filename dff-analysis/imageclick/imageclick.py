import gtk
import pygtk

class ImageClick:

    def destroy(self, widget, data=None):
        ''' Quits gtk
        '''
        self.window.destroy()
        self.image.destroy()
        gtk.main_quit()

    def button_pressed(self, widget, event):
        ''' Event handler assigned to listener. Reads and sets coordinates.
        '''
        if event.type == gtk.gdk.BUTTON_PRESS:
            coords = event.get_coords()
            self.x = int(round(coords[0]))
            self.y = int(round(coords[1]))
            self.destroy(self)
   
    def __init__(self,filename='default.tiff'):
        ''' Creates the window and listener using gtk.
        '''

        self.filename = filename

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

    def main(self):
        ''' Starts gtk.main()
        '''
        gtk.main()