# Tour Guide GUI

This project requires the `gtkmm3` and `mpv` packages to be installed.

Because this GUI uses the GTK API, it can be customized with different GTK themes

https://www.gnome-look.org/browse?cat=135
https://www.gnome-look.org/p/1271140
https://www.gnome-look.org/p/1441725


Currently the binary must be run in this directory as `bin/TGUI` or the media files won't load

TODO:
	Make binary runable with media files anywhere
	fix pixel formatting on ready.gif
	fix alignment of GUI on tablet

## Next Team

All the header files are stored in the `include` folder.
The code in this app should be relatively straightforeward, but official documentation can be found at this site:
https://gtkmm.org/en/documentation.html

Placeholder videos and content can be found in the `media` folder.
Those files can be changed out with more relevant videos that actually give a tour
of the Innovation Design Hub

## Running the Program

In order to run the GUI on the Raspberry Pi, clone this repository and run `make`
in this directory. Once that is done, a compiled program should be runnable by
entering `bin/TGUI` in the command line. The current Raspberry Pi takes advantage
of its graphical environment, LXDE, in order to autorun the program on startup.
