import tkinter as tk
from tkinter import messagebox

# --- Clock display ---
from src.displays.clockDisplay import Clock

# --- Acceleration display ---
from src.sensors.MPU6050 import MPU6050
from src.displays.accelerationDisplay import CarDisplay

# --- GPS map viewer ---
from src.displays.GPSDisplay import OfflineMap
import itertools

from src.displays.temperatureDisplay import SensorOverlay

from src.sensors.LDRLM393 import LightSensor
from src.displays.lightDisplay import LightDisplay

# ===============================================================
# Display Launchers
# ===============================================================

def run_clock():
    """Launch the Clock display."""
    clock = Clock()
    clock.run()


def run_acceleration_display():
    """Launch the 3D car acceleration visualization."""
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


def run_gps_map():
    """Launch the offline map with a moving car."""
    MAP_FOLDER = r"lib/mapNL"
    ZOOM = 14
    TILE_SIZE = 500
    VIEW_SIZE = 800
    UPDATE_INTERVAL = 1000    # milliseconds between updates

    gps_points = [
        (52.0907, 5.1214),
        (52.0910, 5.1225),
        (52.0915, 5.1238),
        (52.0920, 5.1250),
        (52.0923, 5.1262),
        (52.0927, 5.1275),
        (52.0931, 5.1288),
    ]

    gps_cycle = itertools.cycle(gps_points)
    map_viewer = OfflineMap(MAP_FOLDER, zoom=ZOOM, tile_size=TILE_SIZE, view_size=VIEW_SIZE)

    root = tk.Tk()
    root.title("Offline Map Viewer - Moving Car")

    lat, lon = next(gps_cycle)
    img = map_viewer.render_map(lat, lon)
    label = tk.Label(root, image=img)
    label.pack()

    def update_position():
        nonlocal img
        lat, lon = next(gps_cycle)
        img = map_viewer.render_map(lat, lon)
        label.configure(image=img)
        label.image = img
        root.after(UPDATE_INTERVAL, update_position)

    root.after(UPDATE_INTERVAL, update_position)
    root.mainloop()
    
def run_clock_with_sensors(test_mode=False):
    """Launch the clock display with DHT11 temperature & humidity overlay."""
    CAR_PIN = 4
    VENT_PIN = 17

    clock = Clock()
    overlay = SensorOverlay(car_pin=CAR_PIN, vent_pin=VENT_PIN, clock=clock, test_mode=test_mode)
    overlay.update_sensor_data()
    clock.run()
    
def run_light_display(test_mode=False):

    if test_mode:
        sensor = None
    else:
        sensor = LightSensor(pin1=17, pin2=27)

    display = LightDisplay(light_sensor=sensor, test_mode=test_mode)
    display.run()


# ===============================================================
# Main menu (selection window)
# ===============================================================

def main_menu():
    """Simple Tkinter menu to select display mode."""
    root = tk.Tk()
    root.title("Main Display Selector")

    tk.Label(root, text="Select a display mode:", font=("Arial", 14, "bold")).pack(pady=10)

    # Real sensors
    tk.Button(root, text="🕒 Clock + Temp/Humidity (Real Sensors)",
              font=("Arial", 12), width=35,
              command=lambda: [root.destroy(), run_clock_with_sensors(test_mode=False)]).pack(pady=5)

    # Test mode
    tk.Button(root, text="🧪 Clock (Test Mode - No Sensors)",
              font=("Arial", 12), width=35,
              command=lambda: [root.destroy(), run_clock_with_sensors(test_mode=True)]).pack(pady=5)

    tk.Button(root, text="📈 Acceleration Display", font=("Arial", 12),
              width=35, command=lambda: [root.destroy(), run_acceleration_display()]).pack(pady=5)

    tk.Button(root, text="🗺️ GPS Map Viewer", font=("Arial", 12),
              width=35, command=lambda: [root.destroy(), run_gps_map()]).pack(pady=5)
    
    tk.Button(root, text="💡 Light Sensors", font=("Arial", 12), width=25,
          command=lambda: [root.destroy(), run_light_display(test_mode=False)]).pack(pady=5)
    
    tk.Button(root, text="💡 Light Sensors (Test Mode)", font=("Arial", 12), width=25,
          command=lambda: [root.destroy(), run_light_display(test_mode=True)]).pack(pady=5)
    
    tk.Button(root, text="Exit", font=("Arial", 12), width=35,
              command=root.destroy).pack(pady=10)


    root.mainloop()

# ===============================================================
# Entry point
# ===============================================================

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("Exiting...")
