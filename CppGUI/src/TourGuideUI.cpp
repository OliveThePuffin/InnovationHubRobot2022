#include "TourGuideUI.h"
#include <iostream>
using namespace std;

HelloWorld::HelloWorld() : m_button("Hello World")
{
	set_border_width(30);
	m_button.signal_clicked().connect(sigc::mem_fun(*this, &HelloWorld::on_button_clicked));
	add(m_button);
	m_button.show();
}

HelloWorld::~HelloWorld()
{
}

void HelloWorld::on_button_clicked()
{
	cout << "Hello World" << endl;
}
