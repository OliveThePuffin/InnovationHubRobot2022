#!/usr/bin/env python3
import mpv
import locale
import time
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

class TourGuideUI(Gtk.Window):
    def __init__(self):
        self.open = True
        self.window = "none"
        super(TourGuideUI, self).__init__()
        self.fullscreen()
        self.set_keep_above(True)
        self.set_title("TourGuideUI")
        self.set_size_request(1920, 1080)
        #self.set_border_width(30)
        self.connect("destroy", Gtk.main_quit)

    def ready_wait(self):
        # Set up the gif
        image = Gtk.Image()
        width = Gdk.Screen.get_default().get_width()
        height = Gdk.Screen.get_default().get_height()
        if (width == 3840 and height == 2160):
            filename = "ready_wait_4k.gif"
        elif (width == 1920 and height == 1080):
            filename = "ready_wait_1080p.gif"
        else:
            filename = "ready_wait_1080p.gif"
        wait_animation = GdkPixbuf.PixbufAnimation.new_from_file(filename)
        image.set_from_animation(wait_animation)

        # Set up button functionality
        ready_btn = Gtk.Button()
        ready_btn.add(image)
        ready_btn.connect("clicked", Gtk.main_quit)
        self.add(ready_btn)
        self.show_all()

    def intro(self):

        button_width = 1000
        button_height = 700

        button1 = Gtk.Button(label="Room 1")
        button1.set_size_request(button_width, button_height)
        button2 = Gtk.Button(label="Room 2")
        button2.set_size_request(button_width, button_height)
        button3 = Gtk.Button(label="Room 3")
        button3.set_size_request(button_width, button_height)
        button4 = Gtk.Button(label="Room 4")
        button4.set_size_request(button_width, button_height)
        button5 = Gtk.Button(label="Room 5")
        button5.set_size_request(button_width, button_height)
        button6 = Gtk.Button(label="Room 6")
        button6.set_size_request(button_width, button_height)

        grid = Gtk.Grid();
        grid.set_border_width(30)
        grid.add(button1);
        grid.attach(button2, 1, 0, 2, 1);
        grid.attach_next_to(button3, button1, Gtk.PositionType.BOTTOM, 1, 2);
        grid.attach_next_to(button4, button2, Gtk.PositionType.BOTTOM, 2, 1);
        grid.attach(button5, 1, 2, 1, 1);
        grid.attach_next_to(button6, button5, Gtk.PositionType.RIGHT, 1, 1);
        self.add(grid)

        quit_button = Gtk.Button(label="Quit")
        quit_button.set_size_request(600, 600)
        quit_button.connect("clicked", Gtk.main_quit)
        grid.attach(quit_button, 3, 2, 1, 1)

        video = Gtk.Frame()
        grid.attach(video, 3, 1, 1, 1)
        self.show_all()
        self.mpv = mpv.MPV(wid=str(video.get_property("window").get_xid()))
        self.mpv.play("intro.mkv")
        self.mpv.terminate()

    def quit(self):
        Gtk.main_quit()


# Main loop
def main():
    # Wait for user input (a touch)
    locale.setlocale(locale.LC_NUMERIC, 'C')

    ready_wait = TourGuideUI()
    ready_wait.ready_wait()
    Gtk.main()

    # play a welcome video
    intro = TourGuideUI()
    intro.intro()
    Gtk.main()

    # room selection
    #room_select = TourGuideUI()
    #room_select.room_select()
    #room_select.show_all()
    #Gtk.main()

if __name__ == "__main__":
    main()
