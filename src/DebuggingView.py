from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox,
    QPushButton, QHBoxLayout, QCheckBox, QLineEdit
)
from PySide6.QtCore import QTimer

from src.sensors.MPU6050 import MPU6050


class DebuggerWindow(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Dashboard Debugger")
        self.setMinimumWidth(320)

        layout = QVBoxLayout()

        # ===== Helpers =====
        def add_spin(label, minv, maxv, step, prop_get, prop_set):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            spin = QDoubleSpinBox()
            spin.setRange(minv, maxv)
            spin.setSingleStep(step)
            spin.setValue(prop_get())
            spin.valueChanged.connect(lambda v: prop_set(v))
            row.addWidget(spin)
            layout.addLayout(row)

        def add_text(label, prop_get, prop_set):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            field = QLineEdit()
            field.setText(prop_get())
            field.textChanged.connect(lambda v: prop_set(v))
            row.addWidget(field)
            layout.addLayout(row)

        def add_check(label, prop_get, prop_set):
            box = QCheckBox(label)
            box.setChecked(prop_get())
            box.toggled.connect(lambda v: prop_set(v))
            layout.addWidget(box)

        # ===== Fields =====
        add_spin("Velocity (km/h):", 0, 300, 1,
                 lambda: backend.velocity,
                 lambda v: setattr(backend, "velocity", v))

        add_spin("RPM:", 0, 9000, 50,
                 lambda: getattr(backend, "rpm", 0),
                 lambda v: setattr(backend, "rpm", v))

        add_text("GPS Time (HH:MM):",
                 lambda: backend.gpsTime,
                 lambda v: setattr(backend, "gpsTime", v))

        add_spin("Latitude:", -90, 90, 0.0001,
                 lambda: backend.centerLat,
                 lambda v: setattr(backend, "centerLat", v))

        add_spin("Longitude:", -180, 180, 0.0001,
                 lambda: backend.centerLon,
                 lambda v: setattr(backend, "centerLon", v))

        add_spin("Temp Inside (°C):", -10, 60, 0.1,
                 lambda: backend.tempInside,
                 lambda v: setattr(backend, "tempInside", v))

        add_spin("Temp Outside (°C):", -10, 60, 0.1,
                 lambda: backend.tempOutside,
                 lambda v: setattr(backend, "tempOutside", v))

        add_spin("Humidity Inside (%):", 0, 100, 1,
                 lambda: backend.humidityInside,
                 lambda v: setattr(backend, "humidityInside", v))

        add_spin("Humidity Outside (%):", 0, 100, 1,
                 lambda: backend.humidityOutside,
                 lambda v: setattr(backend, "humidityOutside", v))

        add_spin("Pi Temp (°C):", 0, 100, 0.5,
                 lambda: backend.piTemperature,
                 lambda v: setattr(backend, "piTemperature", v))

        add_spin("Accel X:", -5, 5, 0.01,
                 lambda: backend.ax,
                 lambda v: setattr(backend, "ax", v))

        add_spin("Accel Y:", -5, 5, 0.01,
                 lambda: backend.ay,
                 lambda v: setattr(backend, "ay", v))

        add_check("Daytime",
                  lambda: backend.isDaytime,
                  lambda v: setattr(backend, "isDaytime", v))

        # ===== MPU =====
        mpu = MPU6050()
        mpu.initialize()

        # ===== Buttons =====
        btn_view = QPushButton("Bottom button")
        btn_overlay = QPushButton("Top button")
        btn_close = QPushButton("Close")

        layout.addWidget(btn_view)
        layout.addWidget(btn_overlay)
        layout.addWidget(btn_close)

        # ===== Button logic =====
        def cycle_view():
            views = ["gps", "clock", "data", "accel", "techno"]
            try:
                idx = views.index(backend.currentView)
            except ValueError:
                idx = 0
            backend.currentView = views[(idx + 1) % len(views)]
            print("[DEBUGGER] Next view ->", backend.currentView)

        def toggle_overlay():
            if backend.currentView == "accel":
                if backend.calibrationState == "calibrating":
                    print("[INFO] Calibration already in progress")
                    return

                print("[BUTTON] Calibrating MPU6050...")
                backend.calibrationState = "calibrating"
                try:
                    mpu.calibrate_accelerometer()
                    backend.calibrationState = "done"
                except Exception as e:
                    backend.calibrationState = "failed"
                    print("[ERROR]", e)

                QTimer.singleShot(
                    2000,
                    lambda: setattr(backend, "calibrationState", "idle")
                )

            elif backend.currentView == "gps":
                backend.showOverlays = not backend.showOverlays
                print("[BUTTON] Toggle GPS overlay")

            else:
                print("[BUTTON] No action in this view")

        btn_view.clicked.connect(cycle_view)
        btn_overlay.clicked.connect(toggle_overlay)
        btn_close.clicked.connect(self.close)

        self.setLayout(layout)
