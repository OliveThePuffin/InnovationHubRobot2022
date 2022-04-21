# Tour Guide GUI

This project requires the `gtkmm3` and `mpv` packages to be installed.

Because this GUI uses the GTK API, it can be customized with different GTK themes

https://www.gnome-look.org/browse?cat=135
https://www.gnome-look.org/p/1271140
https://www.gnome-look.org/p/1441725


<<<<<<< HEAD
Currently the binary must be run in this dir as `bin/TGUI` or the media files won't load

TODO:
	Make binary runable with media files anywhere
	fix pixel formatting on ready.gif
	fix alignment of GUI on tablet

Feedback: Make room selection layout show current location
=======
Currently the binary must be run the root project directory as `build/TGUI` or the media files won't load

## Next Team

The code in this app should be relatively straightforward, but official documentation of the GTK api can be found at this site:
https://gtkmm.org/en/documentation.html

Placeholder videos and content can be found in the `media` folder.
Those files can be changed out with more relevant videos that actually give a tour
of the Innovation Design Hub

## Running the Program

In order to run the GUI on the Raspberry Pi, clone this repository and run `build.sh`
in this directory. Once that is done, a compiled program should be runnable by
entering `build/TGUI` in the command line. The current Raspberry Pi takes advantage
of its graphical environment, LXDE, in order to autorun the program on startup.
>>>>>>> c89820a2ec4d89f6f46c710b23114b3de0c7214e
