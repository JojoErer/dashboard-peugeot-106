import sys
import itertools
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# --- Imports for displays & sensors ---
from src.displays.clockDisplay import Clock
from src.sensors.MPU6050 import MPU6050
from src.displays.accelerationDisplay import CarDisplay
from src.displays.GPSDisplay import GPSMapWidget # Updated version that returns QImage
from src.displays.temperatureDisplay import SensorOverlay
from src.sensors.LDRLM393 import LightSensor
from src.displays.lightDisplay import LightDisplay

# ===============================================================
# Display Launchers
# ===============================================================

def run_clock():
    Clock().run()

def run_acceleration_display():
    sensor = MPU6050()
    sensor.init_sensor()
    print("Calibrating accelerometer...")
    sensor.calibrate_accelerometer()

    display = CarDisplay(
        obj_file=r"lib/3dModel/Peugeot106Final.obj",
        ax_offset=sensor.ax_offset,
        ay_offset=sensor.ay_offset,
        update_rate=5,
        show_graph=False,
        smoothing=1.0
    )
    display.run(sensor.get_calibrated_acceleration)

def run_clock_with_sensors(test_mode=False):
    CAR_PIN = 17
    VENT_PIN = 27

    clock = Clock()
    overlay = SensorOverlay(car_pin=CAR_PIN, vent_pin=VENT_PIN, clock=clock, test_mode=test_mode)
    overlay.update_sensor_data()
    clock.run()

def run_light_display(test_mode=False):
    sensor = None if test_mode else LightSensor(pin1=22, pin2=10)
    display = LightDisplay(light_sensor=sensor, test_mode=test_mode)
    display.run()

# ===============================================================
# Main Menu Widget
# ===============================================================

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Display Selector")
        self.resize(400, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel("Select a display mode:"))

        # Buttons
        btn_clock_real = QPushButton("🕒 Clock + Temp/Humidity (Real Sensors)")
        btn_clock_test = QPushButton("🧪 Clock (Test Mode - No Sensors)")
        btn_accel = QPushButton("📈 Acceleration Display")
        btn_gps = QPushButton("🗺️ GPS Map Viewer")
        btn_light_real = QPushButton("💡 Light Sensors")
        btn_light_test = QPushButton("💡 Light Sensors (Test Mode)")
        btn_exit = QPushButton("Exit")

        for btn in [btn_clock_real, btn_clock_test, btn_accel, btn_gps, btn_light_real, btn_light_test, btn_exit]:
            layout.addWidget(btn)

        # Connect signals
        btn_clock_real.clicked.connect(lambda: self.launch(run_clock_with_sensors, False))
        btn_clock_test.clicked.connect(lambda: self.launch(run_clock_with_sensors, True))
        btn_accel.clicked.connect(lambda: self.launch(run_acceleration_display))
        btn_gps.clicked.connect(self.launch_gps_map)
        btn_light_real.clicked.connect(lambda: self.launch(run_light_display, False))
        btn_light_test.clicked.connect(lambda: self.launch(run_light_display, True))
        btn_exit.clicked.connect(self.close)

    def launch(self, func, *args):
        self.close()
        func(*args)

    def launch_gps_map(self):
        self.close()
        self.gps_window = GPSMapWidget()
        self.gps_window.show()

# ===============================================================
# Entry Point
# ===============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec())
