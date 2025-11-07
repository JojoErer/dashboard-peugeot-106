# from PySide6.QtGui import QGuiApplication
# from PySide6.QtQml import QQmlApplicationEngine
# import PyQt6.QtCore
# import sys

# app = QGuiApplication(sys.argv)
# engine = QQmlApplicationEngine()

# engine.load("mainPY.qml")

# if not engine.rootObjects():
#     sys.exit(-1)

# sys.exit(app.exec())

import sys
import random
from PySide6.QtCore import QObject, Signal, Property, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import PyQt6.QtCore

# ----- Python backend exposed to QML -----
class DashboardBackend(QObject):
    # Signals must be emitted to notify QML about changes
    velocityChanged = Signal()
    tempInsideChanged = Signal()
    tempOutsideChanged = Signal()
    humidityInsideChanged = Signal()
    humidityOutsideChanged = Signal()
    piTemperatureChanged = Signal()
    gpsTimeChanged = Signal()
    axChanged = Signal()
    ayChanged = Signal()
    centerLatChanged = Signal()
    centerLonChanged = Signal()

    def __init__(self):
        super().__init__()
        self._velocity = 0
        self._tempInside = 0
        self._tempOutside = 0
        self._humidityInside = 0
        self._humidityOutside = 0
        self._piTemperature = 0
        self._gpsTime = "00:00"
        self._ax = 0
        self._ay = 0
        self._centerLat = 52.1070
        self._centerLon = 5.1214

    # ===== Properties =====
    @Property(float, notify=velocityChanged)
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, val):
        if self._velocity != val:
            self._velocity = val
            self.velocityChanged.emit()

    @Property(float, notify=tempInsideChanged)
    def tempInside(self):
        return self._tempInside

    @tempInside.setter
    def tempInside(self, val):
        if self._tempInside != val:
            self._tempInside = val
            self.tempInsideChanged.emit()

    @Property(float, notify=tempOutsideChanged)
    def tempOutside(self):
        return self._tempOutside

    @tempOutside.setter
    def tempOutside(self, val):
        if self._tempOutside != val:
            self._tempOutside = val
            self.tempOutsideChanged.emit()

    @Property(float, notify=humidityInsideChanged)
    def humidityInside(self):
        return self._humidityInside

    @humidityInside.setter
    def humidityInside(self, val):
        if self._humidityInside != val:
            self._humidityInside = val
            self.humidityInsideChanged.emit()

    @Property(float, notify=humidityOutsideChanged)
    def humidityOutside(self):
        return self._humidityOutside

    @humidityOutside.setter
    def humidityOutside(self, val):
        if self._humidityOutside != val:
            self._humidityOutside = val
            self.humidityOutsideChanged.emit()

    @Property(float, notify=piTemperatureChanged)
    def piTemperature(self):
        return self._piTemperature

    @piTemperature.setter
    def piTemperature(self, val):
        if self._piTemperature != val:
            self._piTemperature = val
            self.piTemperatureChanged.emit()

    @Property(str, notify=gpsTimeChanged)
    def gpsTime(self):
        return self._gpsTime

    @gpsTime.setter
    def gpsTime(self, val):
        if self._gpsTime != val:
            self._gpsTime = val
            self.gpsTimeChanged.emit()

    @Property(float, notify=axChanged)
    def ax(self):
        return self._ax

    @ax.setter
    def ax(self, val):
        if self._ax != val:
            self._ax = val
            self.axChanged.emit()

    @Property(float, notify=ayChanged)
    def ay(self):
        return self._ay

    @ay.setter
    def ay(self, val):
        if self._ay != val:
            self._ay = val
            self.ayChanged.emit()

    @Property(float, notify=centerLatChanged)
    def centerLat(self):
        return self._centerLat

    @centerLat.setter
    def centerLat(self, val):
        if self._centerLat != val:
            self._centerLat = val
            self.centerLatChanged.emit()

    @Property(float, notify=centerLonChanged)
    def centerLon(self):
        return self._centerLon

    @centerLon.setter
    def centerLon(self, val):
        if self._centerLon != val:
            self._centerLon = val
            self.centerLonChanged.emit()


# ----- Main Application -----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = DashboardBackend()
    engine.rootContext().setContextProperty("backend", backend)

    # Load QML relative to this script
    import os
    qml_file = os.path.join(os.path.dirname(__file__), "mainPY.qml")
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    # ----- Example: Update values periodically -----
    def update_values():
        backend.velocity = random.uniform(0, 120)
        backend.tempInside = random.uniform(18, 25)
        backend.tempOutside = random.uniform(10, 35)
        backend.humidityInside = random.uniform(30, 70)
        backend.humidityOutside = random.uniform(20, 80)
        backend.piTemperature = random.uniform(30, 60)
        backend.ax = random.uniform(-2, 2)
        backend.ay = random.uniform(-2, 2)
        backend.gpsTime = f"{random.randint(0,23):02}:{random.randint(0,59):02}"
        backend.centerLat = 52.1070 + random.uniform(-0.01, 0.01)
        backend.centerLon = 5.1214 + random.uniform(-0.01, 0.01)

    timer = QTimer()
    timer.timeout.connect(update_values)
    timer.start(1000)  # update every second

    sys.exit(app.exec())
