cmake_minimum_required(VERSION 3.16)

project(GUI VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOMOC ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 6.2 COMPONENTS Quick location positioning REQUIRED)

qt_add_executable(apptest
    main.cpp
)

qt_add_qml_module(apptest
    URI test
    VERSION 1.0
    QML_FILES main.qml 
    QML_FILES GPSView/BottomBar.qml
    QML_FILES GPSView/TopBar.qml
    QML_FILES GPSView/CircleWindow.qml
    RESOURCES lib/peugeot106emblem/PeugeotBlackLogo.png lib/peugeot106emblem/PeugeotSilverLogo.png lib/peugeotLogo/peugeot106Black.png lib/peugeotLogo/peugeot106Silver.png
    QML_FILES AccelerationView/AccelerationView.qml
    QML_FILES ClockView/ClockView.qml DataView/DataView.qml
    QML_FILES DataView/TemperatureAndHumidityGauge.qml
    RESOURCES lib/icons/carIcon.png lib/icons/raspberryPIIcon.png lib/icons/windIcon.png)

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
set_target_properties(apptest PROPERTIES
#    MACOSX_BUNDLE_GUI_IDENTIFIER com.example.apptest
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

target_link_libraries(apptest
    PRIVATE Qt6::Quick
    PRIVATE Qt6::Location
    PRIVATE Qt6::Positioning)

include(GNUInstallDirs)
install(TARGETS apptest
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
