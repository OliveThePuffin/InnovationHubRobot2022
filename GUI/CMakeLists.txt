cmake_minimum_required(VERSION 3.18)
project(TourGuideUI)
add_executable(TGUI src/main.cpp src/TourGuideUI.cpp)

find_package(PkgConfig)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

if (PKG_CONFIG_FOUND)
	pkg_check_modules(GTK "gtkmm-3.0")
	if (GTK_FOUND)
		target_link_libraries(TGUI ${GTK_LIBRARIES})
		add_definitions(${GTK_CFLAGS} ${GTK_CFLAGS_OTHER})
	endif()
endif()
