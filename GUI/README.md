# Tour Guide GUI

This project requires the `gtkmm3` and `mpv` packages to be installed.

Because this GUI uses the GTK API, it can be customized with different GTK themes

https://www.gnome-look.org/browse?cat=135
https://www.gnome-look.org/p/1271140
https://www.gnome-look.org/p/1441725


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
of its graphical environment, BSPWM, in order to autorun the program on startup.

## About the PI

Other apps could be set to startup automatically by adding a command to ~/.config/bspwm/bspwmrc

the keyboard shortcuts for it can be found in ~/.config/sxhkd/sxhkdrc and can be modified to fit your needs
though this file was uploaded to the pi quickly and contains references to some programs which are not installed
