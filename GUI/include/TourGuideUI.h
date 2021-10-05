//#include "TourGuideUI.h"

#ifndef GTKMM_TOUR_GUIDE_UI_H
#define GTKMM_TOUR_GUIDE_UI_H

//execute system shell commands
//string support
#include <stdlib.h>
#include <string>

//GTK widgets to import
//GDK Pixbuf (to show animations)
#include <gtkmm.h>
#include <gdkmm/pixbufanimation.h>

class TourGuideUI : public Gtk::Window
{

	public:
		TourGuideUI();
		virtual ~TourGuideUI();

		//Hard coded screen resolution
		int s_width  =	1920;
		int s_height =	1080;

	private:
		//Member widgets:
		Gtk::Stack	m_stack;
		Gtk::Button	ready_button;
		Gtk::Image	ready_gif;
		Gtk::Frame	intro_frame;

		//misc variables
		//space after for args
		std::string video_player = "mpv --fs ";
		std::string ready_file = "media/ready_4k.gif";
		std::string intro_file = "media/intro-short.mkv";

		//Signal Handlers:
		void goto_next();
};

#endif
