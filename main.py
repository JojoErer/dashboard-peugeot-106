import sys
import os
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
from src.sensors.ButtonHandler import ButtonHandler
from src.DebuggingView import DebuggerWindow
  
class DashboardBackend(QObject):       
    # --- Signals for QML updates ---
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
    gpsConnectedChanged = Signal()
    nextOverlayRequested = Signal()
    calibrationStateChanged = Signal()
    currentViewChanged = Signal()
    showOverlaysChanged = Signal()
    sensorStatusMessageChanged = Signal()

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
        self._isDaytime = True
        self._gpsConnected = False
        self._calibrationState = ""
        self._currentView = "gps"
        self._showOverlays = True
        self._sensorStatusMessage = "Initializing sensors..."

        self.load_settings()

    def show_debugger(self):
        """Open the Debugger popup window."""
        if not hasattr(self, "_debugger") or self._debugger is None:
            self._debugger = DebuggerWindow(self)
        self._debugger.show()
        self._debugger.raise_()
        self._debugger.activateWindow()

    def load_settings(self):
        """Load settings from a file and apply them."""
        settings_file = "settings.txt"
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    self._currentView = lines[0].strip()
                    self._showOverlays = lines[1].strip().lower() == 'true'

                    self.currentViewChanged.emit()
                    self.showOverlaysChanged.emit()
                    print(f"[INFO] Loaded settings: View={self._currentView}, Overlays={self._showOverlays}")
        else:
            print("[INFO] No settings file found. Using default settings.")

    def save_settings(self):
        """Save current settings (view and overlay) to a file."""
        settings_file = "settings.txt"
        with open(settings_file, 'w') as f:
            f.write(f"{self._currentView}\n")
            f.write(f"{'true' if self._showOverlays else 'false'}\n")
        print(f"[INFO] Settings saved: View={self._currentView}, Overlays={self._showOverlays}")

    def calibrate_mpu(self):
        """Trigger MPU6050 calibration."""
        mpu = MPU6050()
        mpu.calibrate_accelerometer()
        self._calibrationState = f"Calibrated: ax={mpu.ax_offset:.2f}, ay={mpu.ay_offset:.2f}, az={mpu.az_offset:.2f}"
        self.calibrationStateChanged.emit()
        print(self._calibrationState)

    def load_mpu_calibration(self):
        """Load MPU6050 calibration data from a file."""
        mpu = MPU6050()
        mpu.load_calibration()

    @Property(str, notify=sensorStatusMessageChanged)
    def sensorStatusMessage(self):
        return self._sensorStatusMessage

    @sensorStatusMessage.setter
    def sensorStatusMessage(self, val):
        if self._sensorStatusMessage != val:
            self._sensorStatusMessage = val
            self.sensorStatusMessageChanged.emit()

    @Property(str, notify=currentViewChanged)
    def currentView(self): return self._currentView
    @currentView.setter
    def currentView(self, val):
        if self._currentView != val:
            self._currentView = val
            self.currentViewChanged.emit()
            self.save_settings()

    @Property(bool, notify=showOverlaysChanged)
    def showOverlays(self): return self._showOverlays
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
            
    @Property(str, notify=calibrationStateChanged)
    def calibrationState(self):
        return self._calibrationState
    @calibrationState.setter
    def calibrationState(self, val):
        if self._calibrationState != val:
            self._calibrationState = val
            self.calibrationStateChanged.emit()

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
            
# ============================================================
#                       MAIN APPLICATION
# ============================================================

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = DashboardBackend()
    engine.rootContext().setContextProperty("backend", backend)

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
        dht = DHT11(car_pin=4, vent_pin=17)
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
        buttons = ButtonHandler(pin_next=18, pin_extra=23)
        if hasattr(buttons, "test_mode") and buttons.test_mode:
            init_status.append("Buttons: simulated")
        else:
            init_status.append("Buttons: real")
    except Exception as e:
        init_errors.append(f"Buttons: {e}")

    # --- Build display message ---
    if init_errors:
        backend.sensorStatusMessage = (
            "⚠ Errors during initialization:\n"
            + "\n".join(init_errors)
            + "\n\nDetected devices:\n"
            + "\n".join(init_status)
        )
    else:
        backend.sensorStatusMessage = (
            "✅ All systems initialized successfully\n"
            + "\n".join(init_status)
        )

    print(backend.sensorStatusMessage)



    # --- Optional: open debugger window on startup ---
    # backend.show_debugger()

    # --- Main periodic update ---
    def update_values():
        # Temp & humidity
        car_temp, car_hum = dht.read_sensor_data("car")
        vent_temp, vent_hum = dht.read_sensor_data("vent")
        if car_temp is not None: backend.tempInside = car_temp
        if car_hum is not None: backend.humidityInside = car_hum
        if vent_temp is not None: backend.tempOutside = vent_temp
        if vent_hum is not None: backend.humidityOutside = vent_hum

        # Light
        light1 = light_sensor.read_light_intensity(light_sensor.pin1)
        light2 = light_sensor.read_light_intensity(light_sensor.pin2)
        backend.isDaytime = light1 > 0 or light2 > 0

        # GPS
        gps_data = gps_reader.get_data()
        if gps_data:
            if gps_data["latitude"] and gps_data["longitude"]:
                backend.centerLat = gps_data["latitude"]
                backend.centerLon = gps_data["longitude"]
            backend.velocity = gps_data.get("speed", 0.0) if gps_data.get("speed", 0.0) >= 3.0 else 0
            backend.gpsTime = gps_data.get("timestamp", "00:00")

        # Acceleration
        ax, ay, _ = mpu.read_accelerometer()
        backend.ax = ax
        backend.ay = ay

        # Pi temp
        def get_cpu_temperature():
            try:
                cpu = CPUTemperature()
                return cpu.temperature
            except Exception:
                return None

        CPUTemp = get_cpu_temperature()
        if CPUTemp is not None:
            backend.piTemperature = CPUTemp
        else:
            backend.piTemperature = random.uniform(35, 55)

        # --- Check button presses ---
        if buttons.is_pressed("next"):
            views = ["gps", "clock", "data", "accel"]
            current_index = views.index(backend.currentView)
            next_index = (current_index + 1) % len(views)
            backend.currentView = views[next_index]
            print("[BUTTON] Next view requested")   
                    
        if buttons.is_pressed("extra"):
            if backend.currentView == "accel":
                # Prevent spamming if already calibrating
                if backend.calibrationState == "calibrating":
                    print("[INFO] Calibration already in progress")
                else:
                    print("[BUTTON] Calibrating MPU6050 accelerometer...")
                    backend.calibrationState = "calibrating"
                    
                    try:
                        mpu.calibrate_accelerometer()
                        print("[INFO] MPU6050 calibration complete")
                        backend.calibrationState = "done"
                    except Exception as e:
                        print(f"[INFO] MPU6050 calibration failed: {e}")
                        backend.calibrationState = "failed"
                    
                    # Reset to idle after 2 seconds
                    QTimer.singleShot(2000, lambda: setattr(backend, "calibrationState", "idle"))
            elif backend.currentView == "gps":
                # Toggle GPS overlay visibility
                backend.showOverlays = not backend.showOverlays
                print("[BUTTON] Toggle GPS overlay")
            else:
                print("[BUTTON] No change in this view.")
                

    timer = QTimer()
    timer.timeout.connect(update_values)
    timer.start(1000)

    sys.exit(app.exec())