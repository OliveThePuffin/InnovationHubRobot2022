//#include "TourGuideUI.h"

#ifndef GTKMM_TOUR_GUIDE_UI_H
#define GTKMM_TOUR_GUIDE_UI_H

#define GENERAL_BORDER_WIDTH	s_height/48
#define MENU_BORDER_WIDTH	s_height/64

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
		const int s_width  =	1920;
		const int s_height =	1080;

	private:
		//Helper functions
		void setup_stack();
		void setup_ready();
		void setup_main_menu();
		void setup_room_select();
		void setup_options();

		//Stack
		Gtk::Stack	m_stack;

		//Ready
		Gtk::Button	ready_button;
		Gtk::Image	ready_gif;

		//Main Menu
		Gtk::VBox	main_menu;
		Gtk::Button	main_tour;
		Gtk::Button	main_select;
		Gtk::Button	main_options;
		Gtk::Button	main_quit;

		//Room Select
		Gtk::Grid	room_grid;
		Gtk::Image	room_layout;
		Gtk::Button	room_capstone;
		Gtk::Button	room_composites;
		Gtk::Button	room_electronics;
		Gtk::Button	room_cornerstone;
		Gtk::Button	room_cafe;
		Gtk::Button	room_metals;
		Gtk::Button	room_wood;
		Gtk::Button	room_back_button;

		//Options
		Gtk::Grid	options_grid;
		Gtk::Button	options_back_button;

		//Media files
		std::string video_player = "mpv --fs ";
		std::string ready_file = "media/ready.gif";
		std::string floor1_layout = "media/floor1.png";
		std::string intro_file = "media/intro.mkv";

		//Signal Handlers:
		void goto_menu(bool intro);
		void goto_rooms();
		void goto_options();
};

#endif
