//#include <python3.10/Python.h>
#include "TourGuideUI.h"

TourGuideUI::TourGuideUI() //: m_button("Hello World")
{
	//Set up Window
	this->add(m_stack);
	this->fullscreen();

	//Set up elements
	this->setup_stack();
	this->setup_ready();
	this->setup_main_menu();
	this->setup_room_select();
	this->setup_options();

	//show window
	this->show_all();
}

TourGuideUI::~TourGuideUI()
{
}

void TourGuideUI::setup_stack()
{
	m_stack.set_transition_type(Gtk::STACK_TRANSITION_TYPE_CROSSFADE);
	m_stack.set_transition_duration(250);
	m_stack.add(ready_button, "Ready");
	m_stack.add(main_menu, "Main Menu");
	m_stack.add(room_grid, "Room Select");
	m_stack.add(options_grid, "Options");
}

void TourGuideUI::setup_ready()
{
	//Set up Ready Screen
	ready_button.add(ready_gif);
	ready_button.signal_clicked().connect(sigc::bind(sigc::mem_fun(*this,
				&TourGuideUI::goto_menu), true));
	ready_gif.set(Gdk::PixbufAnimation::create_from_file(ready_file));
}

void TourGuideUI::setup_main_menu()
{
	//Set up main menu
	main_menu.set_border_width(GENERAL_BORDER_WIDTH);

	main_tour.set_label("Full Tour");
	main_tour.set_border_width(MENU_BORDER_WIDTH);
	main_tour.signal_clicked().connect(sigc::mem_fun(*this,
				&TourGuideUI::start_master_control));

	main_select.set_label("Room Select");
	main_select.set_border_width(MENU_BORDER_WIDTH);
	main_select.signal_clicked().connect(sigc::mem_fun(*this,
				&TourGuideUI::goto_rooms));

	main_options.set_label("Options");
	main_options.set_border_width(MENU_BORDER_WIDTH);
	main_options.signal_clicked().connect(sigc::mem_fun(*this,
				&TourGuideUI::goto_options));

	main_quit.set_label("Quit");
	main_quit.set_border_width(MENU_BORDER_WIDTH);
	main_quit.signal_clicked().connect(sigc::mem_fun(*this,
				&TourGuideUI::close));

	main_menu.add(main_tour);
	main_menu.add(main_select);
	main_menu.add(main_options);
	main_menu.add(main_quit);
}

void TourGuideUI::setup_room_select()
{

	Glib::RefPtr<Gdk::Pixbuf> pixbuf = Gdk::Pixbuf::create_from_file(floor1_layout);
	pixbuf = pixbuf.get()->scale_simple(
			(s_width - (5*GENERAL_BORDER_WIDTH))/2,
			(s_height - (6*GENERAL_BORDER_WIDTH))/4,
			Gdk::INTERP_BILINEAR);
	room_layout.set(pixbuf);

	room_capstone.set_label("Capstone");
	room_composites.set_label("Composites");
	room_electronics.set_label("Electr\nonics");
	room_cornerstone.set_label("Cornerstone");
	room_cafe.set_label("Cafe");
	room_metals.set_label("Metals");
	room_wood.set_label("Wood");
	room_back_button.set_label("Back");

	room_grid.set_border_width(GENERAL_BORDER_WIDTH);
	room_grid.set_row_homogeneous(true);
	room_grid.set_row_spacing(GENERAL_BORDER_WIDTH);
	room_grid.set_column_homogeneous(true);

	room_grid.attach(room_layout, 0, 0, 9, 2);
	room_grid.attach(room_capstone, 0, 2, 4, 1);
	room_grid.attach_next_to(room_composites, room_capstone, Gtk::POS_RIGHT, 2, 1);
	room_grid.attach_next_to(room_electronics, room_composites, Gtk::POS_RIGHT, 1, 1);
	room_grid.attach_next_to(room_cornerstone, room_electronics, Gtk::POS_RIGHT, 2, 1);
	room_grid.attach(room_cafe, 0, 3, 2, 1);
	room_grid.attach_next_to(room_metals, room_cafe, Gtk::POS_RIGHT, 3, 1);
	room_grid.attach_next_to(room_wood, room_metals, Gtk::POS_RIGHT, 3, 1);
	room_grid.attach_next_to(room_back_button, room_wood, Gtk::POS_RIGHT, 1, 1);
	room_back_button.signal_clicked().connect(sigc::bind(sigc::mem_fun
				(*this, &TourGuideUI::goto_menu), false));
}

void TourGuideUI::setup_options()
{
	options_grid.set_row_homogeneous(true);
	options_grid.set_column_homogeneous(true);
	options_grid.set_border_width(GENERAL_BORDER_WIDTH);

	options_test_button.set_label("Camera Feed");
	options_back_button.set_label("Back");

	options_grid.add(options_back_button);
	options_grid.add(options_test_button);

	options_test_button.signal_clicked().connect(sigc::mem_fun(*this,
				&TourGuideUI::camera_feed));
	options_back_button.signal_clicked().connect(sigc::bind(sigc::mem_fun
				(*this,	&TourGuideUI::goto_menu), false));
}

void TourGuideUI::goto_menu(bool play_intro)
{
	if (play_intro)
		system(video_player.append(intro_file).c_str());
	m_stack.set_visible_child("Main Menu");
}

void TourGuideUI::goto_rooms()
{
	m_stack.set_visible_child("Room Select");
}

void TourGuideUI::goto_options()
{
	m_stack.set_visible_child("Options");
}

void TourGuideUI::start_master_control()
{
	system(python_interpreter.append(master_control_py).c_str());
}

void TourGuideUI::camera_feed()
{
	system(python_interpreter.append(camera_feed_py).c_str());
}
