//#include "TourGuideUI.h"

#ifndef GTKMM_TOUR_GUIDE_UI_H
#define GTKMM_TOUR_GUIDE_UI_H

//GTK widgets to import
#include <gtkmm/window.h>
#include <gtkmm/stack.h>
#include <gtkmm/button.h>
#include <gtkmm/image.h>
#include <gtkmm/frame.h>
#include <mpv/client.h>
//GDK Pixbuf (to show animations)
#include <gdkmm/pixbufanimation.h>
#include <string>

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
		//FILES NEED TO BE SET FROM PWD
		std::string ready_file = "media/ready_4k.gif";
		std::string intro_file = "media/intro-short.mkv";

		//Signal Handlers:
		void goto_next();
};

#endif
