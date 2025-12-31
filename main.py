import sys
import os
from pathlib import Path
import random
from gpiozero import CPUTemperature
from PySide6.QtCore import QObject, Signal, Property, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import PyQt6.QtCore

from src.sensors.DHT11 import DHT11
from src.sensors.LDRLM393 import LDRLM393
from src.sensors.VK162GPS import VK162GPS
from src.sensors.MPU6050 import MPU6050
from src.sensors.RPMreader import RPMreader
from src.sensors.ButtonHandler import ButtonHandler
from src.DebuggingView import DebuggerWindow
from src.gitUpdater import GitUpdater

APP_VERSION = "1.1.0"

# ============================================================
#                     DASHBOARD BACKEND
# ============================================================

class DashboardBackend(QObject):
    velocityChanged = Signal()
    gpsTimeChanged = Signal()
    centerLatChanged = Signal()
    centerLonChanged = Signal()
    tempInsideChanged = Signal()
    tempOutsideChanged = Signal()
    humidityInsideChanged = Signal()
    humidityOutsideChanged = Signal()
    piTemperatureChanged = Signal()
    axChanged = Signal()
    ayChanged = Signal()
    isDaytimeChanged = Signal()
    rpmChanged = Signal()
    gpsConnectedChanged = Signal()

    currentViewChanged = Signal()
    showOverlaysChanged = Signal()
    sensorStatusMessageChanged = Signal()
    
    systemActionStateChanged = Signal()

    def __init__(self):
        super().__init__()

        self._velocity = 0.0
        self._gpsTime = "00:00"
        self._centerLat = 52.1070
        self._centerLon = 5.1214
        self._tempInside = 0.0
        self._tempOutside = 0.0
        self._humidityInside = 0.0
        self._humidityOutside = 0.0
        self._piTemperature = 0.0
        self._ax = 0.0
        self._ay = 0.0
        self._rpm = 0.0
        self._isDaytime = True
        self._gpsConnected = False

        self._currentView = "gps"
        self._showOverlays = True
        self._sensorStatusMessage = "Initializing sensors..."

        self._systemActionState = "idle"

        self.load_settings()

    # --------------------------------------------------------
    # Debugger
    # --------------------------------------------------------

    def show_debugger(self):
        if not hasattr(self, "_debugger") or self._debugger is None:
            self._debugger = DebuggerWindow(self, git_updater)
        self._debugger.show()
        self._debugger.raise_()
        self._debugger.activateWindow()

    # --------------------------------------------------------
    # Settings
    # --------------------------------------------------------

    def load_settings(self):
        if os.path.exists("settings.txt"):
            with open("settings.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    self._currentView = lines[0].strip()
                    self._showOverlays = lines[1].strip().lower() == "true"
                    self.currentViewChanged.emit()
                    self.showOverlaysChanged.emit()

    def save_settings(self):
        with open("settings.txt", "w") as f:
            f.write(f"{self._currentView}\n")
            f.write(f"{'true' if self._showOverlays else 'false'}\n")

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------

    @Property(str, notify=sensorStatusMessageChanged)
    def sensorStatusMessage(self):
        return self._sensorStatusMessage

    @sensorStatusMessage.setter
    def sensorStatusMessage(self, val):
        if self._sensorStatusMessage != val:
            self._sensorStatusMessage = val
            self.sensorStatusMessageChanged.emit()
            
    @Property(str, notify=systemActionStateChanged)
    def systemActionState(self):
        return self._systemActionState
    
    @systemActionState.setter
    def systemActionState(self, val):
        if self._systemActionState != val:
            self._systemActionState = val
            self.systemActionStateChanged.emit()

    @Property(str, notify=currentViewChanged)
    def currentView(self):
        return self._currentView

    @currentView.setter
    def currentView(self, val):
        if self._currentView != val:
            self._currentView = val
            self.currentViewChanged.emit()
            self.save_settings()

    @Property(bool, notify=showOverlaysChanged)
    def showOverlays(self):
        return self._showOverlays

    @showOverlays.setter
    def showOverlays(self, val):
        if self._showOverlays != val:
            self._showOverlays = val
            self.showOverlaysChanged.emit()
            self.save_settings()

    @Property(float, notify=velocityChanged)
    def velocity(self): return self._velocity
    @velocity.setter
    def velocity(self, val):
        if self._velocity != val:
            self._velocity = val
            self.velocityChanged.emit()

    @Property(str, notify=gpsTimeChanged)
    def gpsTime(self): return self._gpsTime
    @gpsTime.setter
    def gpsTime(self, val):
        if self._gpsTime != val:
            self._gpsTime = val
            self.gpsTimeChanged.emit()

    @Property(float, notify=centerLatChanged)
    def centerLat(self): return self._centerLat
    @centerLat.setter
    def centerLat(self, val):
        if self._centerLat != val:
            self._centerLat = val
            self.centerLatChanged.emit()

    @Property(float, notify=centerLonChanged)
    def centerLon(self): return self._centerLon
    @centerLon.setter
    def centerLon(self, val):
        if self._centerLon != val:
            self._centerLon = val
            self.centerLonChanged.emit()

    @Property(float, notify=tempInsideChanged)
    def tempInside(self): return self._tempInside
    @tempInside.setter
    def tempInside(self, val):
        if self._tempInside != val:
            self._tempInside = val
            self.tempInsideChanged.emit()

    @Property(float, notify=tempOutsideChanged)
    def tempOutside(self): return self._tempOutside
    @tempOutside.setter
    def tempOutside(self, val):
        if self._tempOutside != val:
            self._tempOutside = val
            self.tempOutsideChanged.emit()

    @Property(float, notify=humidityInsideChanged)
    def humidityInside(self): return self._humidityInside
    @humidityInside.setter
    def humidityInside(self, val):
        if self._humidityInside != val:
            self._humidityInside = val
            self.humidityInsideChanged.emit()

    @Property(float, notify=humidityOutsideChanged)
    def humidityOutside(self): return self._humidityOutside
    @humidityOutside.setter
    def humidityOutside(self, val):
        if self._humidityOutside != val:
            self._humidityOutside = val
            self.humidityOutsideChanged.emit()

    @Property(float, notify=piTemperatureChanged)
    def piTemperature(self): return self._piTemperature
    @piTemperature.setter
    def piTemperature(self, val):
        if self._piTemperature != val:
            self._piTemperature = val
            self.piTemperatureChanged.emit()

    @Property(float, notify=axChanged)
    def ax(self): return self._ax
    @ax.setter
    def ax(self, val):
        if self._ax != val:
            self._ax = val
            self.axChanged.emit()

    @Property(float, notify=ayChanged)
    def ay(self): return self._ay
    @ay.setter
    def ay(self, val):
        if self._ay != val:
            self._ay = val
            self.ayChanged.emit()

    @Property(bool, notify=isDaytimeChanged)
    def isDaytime(self): return self._isDaytime
    @isDaytime.setter
    def isDaytime(self, val):
        if self._isDaytime != val:
            self._isDaytime = val
            self.isDaytimeChanged.emit()
            
    @Property(float, notify=rpmChanged)
    def rpm(self):
        return self._rpm
    @rpm.setter
    def rpm(self, val):
        if self._rpm != val:
            self._rpm = val
            self.rpmChanged.emit()

            
# ============================================================
#                       MAIN APPLICATION
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = DashboardBackend()
    engine.rootContext().setContextProperty("backend", backend)
    
    # -------------------------------
    # Git updater
    # -------------------------------
    def get_app_version():
        return APP_VERSION

    # Initialize GitUpdater with status_callback updating sensorStatusMessage
    git_updater = GitUpdater(
        repo_path=os.path.dirname(__file__),  # Assuming repo is main project folder
        version_getter=get_app_version,
        status_callback=lambda msg: setattr(backend, 'sensorStatusMessage', msg)
    )
    
    debugOn = True
    engine.rootContext().setContextProperty("debugOn", debugOn)

    qml_file = os.path.join(os.path.dirname(__file__), "src/dashboardGUI/main.qml")
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    # --- Initialize sensors ---
    print("Initializing sensors...")
    init_errors = []
    init_status = []

    # --- DHT11 ---
    try:
        dht = DHT11(car_pin=4, vent_pin=27)
        if hasattr(dht, "test_mode") and dht.test_mode:
            init_status.append("DHT11: simulated")
        else:
            init_status.append("DHT11: real")
    except Exception as e:
        init_errors.append(f"DHT11: {e}")

    # --- LDR Light Sensor ---
    try:
        light_sensor = LDRLM393(pin1=22, pin2=10)
        light_sensor.initialize()
        if hasattr(light_sensor, "test_mode") and light_sensor.test_mode:
            init_status.append("LDR: simulated")
        else:
            init_status.append("LDR: real")
    except Exception as e:
        init_errors.append(f"LDR: {e}")
        
    # --- RPM ---
    try:
        rpm_reader = RPMreader(pin=17, pulses_per_revolution=1)
        if rpm_reader.test_mode:
            init_status.append("RPM: simulated")
        else:
            init_status.append("RPM: real")
    except Exception as e:
        init_errors.append(f"RPM: {e}")

    # --- GPS ---
    try:
        gps_reader = VK162GPS()
        gps_reader.initialize()
        backend.gpsConnected = not gps_reader.test_mode
        if hasattr(gps_reader, "test_mode") and gps_reader.test_mode:
            init_status.append("GPS: simulated")
        else:
            init_status.append("GPS: real")
    except Exception as e:
        init_errors.append(f"GPS: {e}")

    # --- MPU6050 (Accelerometer) ---
    try:
        mpu = MPU6050()
        mpu.initialize()
        if hasattr(mpu, "test_mode") and mpu.test_mode:
            init_status.append("MPU6050: simulated")
        else:
            init_status.append("MPU6050: real")
    except Exception as e:
        init_errors.append(f"MPU6050: {e}")

    # --- Buttons ---
    try:
        buttons = ButtonHandler(pin_next=5, pin_extra=6)
        if hasattr(buttons, "test_mode") and buttons.test_mode:
            init_status.append("Buttons: simulated")
        else:
            init_status.append("Buttons: real")
    except Exception as e:
        init_errors.append(f"Buttons: {e}")

    # --- Build display message ---
    if init_errors:
        backend.sensorStatusMessage = (
            "Errors during initialization:\n"
            + "\n".join(init_errors)
            + "\n\nDetected devices:\n"
            + "\n".join(init_status)
        )
    else:
        backend.sensorStatusMessage = (
            "All systems initialized successfully\n"
            + "\n".join(init_status)
        )

    print(backend.sensorStatusMessage)
    
    # --- Optional: open debugger window on startup ---
    if debugOn:
        backend.show_debugger()

    # --- Main periodic update ---
    def update_values():
        try:
            # --- Light Sensor ---
            try:
                light1 = light_sensor.read_light_intensity(light_sensor.pin1)
                light2 = light_sensor.read_light_intensity(light_sensor.pin2)
                backend.isDaytime = light1 > 0 or light2 > 0
            except Exception as e:
                backend.sensorStatusMessage = f"LDR read error: {e}"

            # --- GPS ---
            try:
                gps_data = gps_reader.get_data()
                if gps_data:
                    if gps_data["latitude"] and gps_data["longitude"]:
                        backend.centerLat = gps_data["latitude"]
                        backend.centerLon = gps_data["longitude"]
                    backend.velocity = gps_data.get("speed", 0.0) if gps_data.get("speed", 0.0) >= 3.0 else 0
                    backend.gpsTime = gps_data.get("timestamp", "00:00")
            except Exception as e:
                backend.sensorStatusMessage = f"GPS read error: {e}"

            # --- Acceleration ---
            if backend.currentView == "accel":
                try:
                    ax, ay, _ = mpu.get_calibrated_acceleration()
                    backend.ax = ax
                    backend.ay = ay
                except Exception as e:
                    backend.sensorStatusMessage = f"MPU6050 read error: {e}"

            # --- RPM ---
            if backend.currentView == "techno":
                try:
                    rpm = rpm_reader.read_rpm()
                    backend.rpm = rpm
                except Exception as e:
                    backend.sensorStatusMessage = f"RPM read error: {e}"

            # --- Pi Temp and DHT11 ---
            if backend.currentView == "data":
                try:
                    cpu_temp = CPUTemperature().temperature
                    backend.piTemperature = cpu_temp if cpu_temp else random.uniform(35, 55)
                except Exception:
                    backend.piTemperature = random.uniform(35, 55)
                try:
                    car_temp, car_hum = dht.read_sensor_data("car")
                    vent_temp, vent_hum = dht.read_sensor_data("vent")
                    if car_temp is not None: backend.tempInside = car_temp
                    if car_hum is not None: backend.humidityInside = car_hum
                    if vent_temp is not None: backend.tempOutside = vent_temp
                    if vent_hum is not None: backend.humidityOutside = vent_hum
                except Exception as e:
                    backend.sensorStatusMessage = f"DHT11 read error: {e}"

            # --- Buttons ---
            if buttons.is_pressed("next"):
                views = ["gps", "clock", "data", "accel", "techno"]
                current_index = views.index(backend.currentView)
                next_index = (current_index + 1) % len(views)
                backend.currentView = views[next_index]
                backend.systemActionState = f"Switched to view {backend.currentView}"

            if buttons.is_pressed("extra"):
                if backend.currentView == "data":
                    if backend.systemActionState != "idle":
                        print("[INFO] System busy:", backend.systemActionState)
                        return

                    print("[DEBUGGER] Git update requested")
                    backend.sensorStatusMessage = "Checking for updates..."
                    backend.systemActionState = "git_checking"
                    git_updater.handle_update_request()
                elif backend.currentView == "accel":
                    if getattr(backend, "calibrationState", None) == "calibrating":
                        backend.systemActionState = "MPU6050 calibration already in progress"
                    else:
                        backend.systemActionState = "Calibrating MPU6050..."
                        backend.calibrationState = "calibrating"
                        try:
                            mpu.calibrate_accelerometer()
                            backend.calibrationState = "done"
                            backend.systemActionState = "MPU6050 calibration done"
                        except Exception as e:
                            backend.calibrationState = "failed"
                            backend.systemActionState = f"MPU6050 calibration failed: {e}"
                elif backend.currentView == "gps":
                    backend.showOverlays = not backend.showOverlays
                    backend.systemActionState = f"GPS overlays {'shown' if backend.showOverlays else 'hidden'}"
                elif backend.currentView == "clock":
                    backend.systemActionState = "Shutting down..."
                    os.system("sudo shutdown now")
                else:
                    backend.systemActionState = "No action for this view"

        except Exception as e:
            backend.sensorStatusMessage = f"Unexpected error: {e}"
            backend.systemActionState = "error"
            
    timer = QTimer()
    if not debugOn:
        timer.timeout.connect(update_values)
    timer.start(500)

    sys.exit(app.exec())