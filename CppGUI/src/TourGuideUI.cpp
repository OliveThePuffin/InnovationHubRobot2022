#include "TourGuideUI.h"

TourGuideUI::TourGuideUI() //: m_button("Hello World")
{
	//Set up Window
	this->add(m_stack);
	this->set_border_width(10);
	this->fullscreen();

	//Set up the Stack
	m_stack.add(ready_button, "Ready");
	m_stack.add(intro_frame, "Intro");

	//Set up Ready Screen
	ready_button.add(ready_gif);
	ready_button.signal_clicked().
		connect(sigc::mem_fun(*this, &TourGuideUI::goto_next));
	ready_gif.set(Gdk::PixbufAnimation::create_from_file(ready_file));

	//Set up intro video

	//show window
	this->show_all();
}

TourGuideUI::~TourGuideUI()
{
}

void TourGuideUI::goto_next()
{
	std::string current_widget = m_stack.get_visible_child_name();

	if (current_widget == "Ready")
		m_stack.set_visible_child("Intro");	
	else if (current_widget == "Intro")
		this->close();
	else
		this->close();
}
