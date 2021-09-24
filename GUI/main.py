#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class TourGuideUI(Gtk.Window):
    def __init__(self):
        self.window = "none"
        super(TourGuideUI, self).__init__()

    def init_ui(self):
        #grid = Gtk.Grid()
        #self.add(grid)
        self.fullscreen()
        self.set_keep_above(True)
        self.set_title("TourGuideUI")
        self.set_size_request(250, 180)

        self.set_border_width(30)
        self.connect("destroy", Gtk.main_quit)

    def init_wait(self):
        grid = Gtk.Grid()
        self.add(grid)
        ok_btn = Gtk.Button(label="Ready")
        ok_btn.set_size_request(80, 30)
        ok_btn.connect("clicked", self.on_button_clicked)
        grid.attach(ok_btn, 0, 0, 1, 1)

    def room_select(self):
        self.remove(grid)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(1000)
        
        #checkbutton stack
        checkbutton = Gtk.CheckButton(label="Click me!")
        stack.add_titled(checkbutton, "check", "Check Button")
        
        #label stack
        label = Gtk.Label()
        label.set_markup("<big>A fancy label</big>")
        stack.add_titled(label, "label", "A label")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        vbox.pack_start(stack_switcher, True, True, 0)
        vbox.pack_start(stack, True, True, 0)

        #label = Gtk.Label("Where do you want to go?")
        #grid.attach(label, 0, 0, 1, 1)
    def on_button_clicked(self, widget):
        self.room_select()
        #Gtk.main_quit()

# Main menu


# Language selection


# Room to go to


# Main loop
def main():
    win = TourGuideUI()
    win.init_ui()
    win.init_wait()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
