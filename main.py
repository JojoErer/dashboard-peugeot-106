from src.displays.clockDisplay import Clock

# Create an instance of the Clock class
# clock = Clock()
# clock.run()

# main.py
from src.sensors.MPU6050 import MPU6050
from src.displays.accelerationDisplay import CarDisplay

def main():
    sensor = MPU6050()
    sensor.init_sensor()

    print("Calibrating accelerometer...")
    sensor.calibrate_accelerometer()

    display = CarDisplay(
        obj_file = r"lib/3dModel/Peugeot106Final.obj",
        ax_offset=sensor.ax_offset,
        ay_offset=sensor.ay_offset,
        update_rate=5,
        show_graph=False,
        smoothing=1.0
    )

    display.run(sensor.get_calibrated_acceleration)

if __name__ == "__main__":
    main()