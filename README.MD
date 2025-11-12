**Dashboard Peugeot 106**

This Git contains the code for a replacement screen for the clock in the dashboard of a Peugeot 106 ph2.
It can also replace the tachnometer that other models have. 

Current features are:
- Shows current time (digital and analog) based on a GPS signal.
- Shows current location and velocitiy based on a GPS signal.
- Shows offline map based on current position (cannot be used for navigation).
- Shows temperature and humidity of 2 sensors, which are placed in the car and car ventilation.
- Shows acceleration of the car in 2 dimensions. 

The code is written in Python and uses PyQt6 and Pyside6 for the GUI. The code is highly customizable and can be easily adapted for other sensors, data and graphical interfaces. A simple debugger class is added for development on a pc. It is not needed to install any other programs to run the interface: Run the setup.py to install the required packages in a virtual environment. 

When changing the GUI (.qml) files, it is best to install the QT creator application (https://doc.qt.io/qtcreator/), which allows for simple, direct updates of the GUI, while changing the layout. The QT creator can open the dashboardGUI folder and create an executable and debug files for simple editing.

The offline map is not part of this repository, but must be an XYZ maptiles layout, and can be most easily downloaded (as .png files) with the QGIS application (https://qgis.org/), which allows for easy selection of the desired map with OSM data. It can also be used for other offline map formats (eg satallite maps), but those source files have to be downloaded elsewhere. The XYZ .png files must be placed in a /map folder in the /lib directory

Lightsensors are used to detect if the main light of the car is turned on or off. This ensures that the display is in day/night mode and has a similar colour as the (analog) velocity gauge. It was chosen to use a light sensor instead of acquiring the system from the car to decrease the risk of damaging the ECU. 

The code is optimised for the following hardware:
- Raspberry Pi 3b
- MPU6050 accelerometer
- VK162G GPS (via USB)
- DHT11 temperature and humidity sensor
- LDRLM393 light sensor (digital output)
- Wisecoco 3.4 inch 800X800 round TFT display (https://nl.aliexpress.com/i/1005004123860204.html)

Other required components are:
- jumper wires
- 5 V power source (provided via usb in the sigarrete plug).
- push buttons

Important aspects to consider:
- The import of PyQt6 in the main.py cannot be removed, it is required to find missing .dll files.
- Ensure that the .venv is activated before running the program.
- If a standalone .exe is required for the qml interface run: C:\Qt\6.10.0\mingw_64\bin\windeployqt.exe build\dashboardGUI.exe
  (from the location where Qt is installed)
- This exe is standalone, but does not work on the Raspberry Pi.

Future improvements:
- Read data from the tachnometer and display it in a new view. This, probably, requires a analog to digital converter, but the car provides this signal and if it is a PDM signal, it can be read relatively easily.
- Update the view to have various options and layouts.
- Updat the offline map with other map types.
- Further integration with the car by displaying other ECU sensor data. 