import sys
import os
import random
from gpiozero import CPUTemperature
from PySide6.QtCore import QObject, Signal, Property, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import PyQt6.QtCore
import concurrent.futures

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
    dayColorChanged = Signal()
    gpsConnectedChanged = Signal()
    nextViewRequested = Signal()
    nextOverlayRequested = Signal()
    calibrationStateChanged = Signal()

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
    
    def show_debugger(self):
        """Open the Debugger popup window."""
        if not hasattr(self, "_debugger") or self._debugger is None:
            self._debugger = DebuggerWindow(self)
        self._debugger.show()
        self._debugger.raise_()
        self._debugger.activateWindow()


    # --- Properties (same as before) ---
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
            self.dayColorChanged.emit()

    @Property(str, notify=dayColorChanged)
    def dayColor(self):
        return "white" if self._isDaytime else "yellow"

    @Property(bool, notify=gpsConnectedChanged)
    def gpsConnected(self): return self._gpsConnected
    @gpsConnected.setter
    def gpsConnected(self, val):
        if self._gpsConnected != val:
            self._gpsConnected = val
            self.gpsConnectedChanged.emit()


# ============================================================
#                       MAIN APPLICATION
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    backend = DashboardBackend()
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = os.path.join(os.path.dirname(__file__), "dashboardGUI/mainPY.qml")
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)

    # --- Initialize sensors ---
    print("🔧 Initializing sensors...")
    dht = DHT11(car_pin=4, vent_pin=17)
    light_sensor = LDRLM393(pin1=22, pin2=10)
    light_sensor.initialize()

    gps_reader = VK162GPS()
    gps_reader.initialize()
    backend.gpsConnected = not gps_reader.test_mode

    mpu = MPU6050()
    mpu.initialize()

    buttons = ButtonHandler(pin_next=18, pin_extra=23)
    
    # --- Optional: open debugger window on startup ---
    backend.show_debugger()


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
        backend.isDaytime = ((light1 + light2) / 2.0) >= 0.5

        # GPS
        gps_data = gps_reader.get_data()
        if gps_data:
            if gps_data["latitude"] and gps_data["longitude"]:
                backend.centerLat = gps_data["latitude"]
                backend.centerLon = gps_data["longitude"]
            backend.velocity = gps_data.get("speed", 0.0)
            backend.gpsTime = gps_data.get("timestamp", "00:00")

        # Acceleration
        ax, ay, az = mpu.read_accelerometer()
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
            backend.nextViewRequested.emit()
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
                        print("✅ MPU6050 calibration complete")
                        backend.calibrationState = "done"
                    except Exception as e:
                        print(f"❌ MPU6050 calibration failed: {e}")
                        backend.calibrationState = "failed"
                    
                    # Reset to idle after 2 seconds
                    QTimer.singleShot(2000, lambda: setattr(backend, "calibrationState", "idle"))
            else:
                backend.nextOverlayRequested.emit()
                print("[BUTTON] Next overlay requested")
                

    timer = QTimer()
    #timer.timeout.connect(update_values)
    timer.start(1000)

    sys.exit(app.exec())