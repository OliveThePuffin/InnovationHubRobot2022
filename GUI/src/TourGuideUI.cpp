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
	//ready_button.set_border_width(GENERAL_BORDER_WIDTH);
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
	room_grid.set_row_spacing(s_height/10);
	room_grid.set_column_homogeneous(true);
	//room_grid.set_column_spacing(ROOM_BUTTON_WIDTH);

	room_grid.attach(room_capstone, 0, 0, 4, 1);
	room_grid.attach_next_to(room_composites, room_capstone, Gtk::POS_RIGHT, 2, 1);
	room_grid.attach_next_to(room_electronics, room_composites, Gtk::POS_RIGHT, 1, 1);
	room_grid.attach_next_to(room_cornerstone, room_electronics, Gtk::POS_RIGHT, 2, 1);
	room_grid.attach(room_cafe, 0, 1, 2, 1);
	room_grid.attach_next_to(room_metals, room_cafe, Gtk::POS_RIGHT, 3, 1);
	room_grid.attach_next_to(room_wood, room_metals, Gtk::POS_RIGHT, 3, 1);
	room_grid.attach_next_to(room_back_button, room_wood, Gtk::POS_RIGHT, 1, 1);
	room_back_button.signal_clicked().connect(sigc::bind(sigc::mem_fun
				(*this, &TourGuideUI::goto_menu), false));
}

void TourGuideUI::setup_options()
{
	options_back_button.set_label("Back");
	//options_back_button.set_size_request
	//	(ROOM_BUTTON_WIDTH, ROOM_BUTTON_HEIGHT);
	options_grid.set_border_width(GENERAL_BORDER_WIDTH);
	options_grid.add(options_back_button);
	options_back_button.signal_clicked().connect(sigc::bind(sigc::mem_fun
				(*this,	&TourGuideUI::goto_menu), false));
}

void TourGuideUI::goto_menu(bool intro)
{
	//if (intro)
	//	system(video_player.append(intro_file).c_str());
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
