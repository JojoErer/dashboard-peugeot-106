import time
import random
import os

class MPU6050:
    def __init__(self):
        """Initialize the MPU6050 sensor or enable simulation mode if unavailable."""
        self.SMBUS_AVAILABLE = False
        self.MPU_CONNECTED = False
        self.bus = None
        self.test_mode = False

        try:
            import smbus2
            self.bus = smbus2.SMBus(1)
            self.SMBUS_AVAILABLE = True
        except (ImportError, FileNotFoundError):
            self.test_mode = True
            print("[INFO] smbus not found. Running in simulation mode.")

        # MPU6050 register addresses
        self.MPU6050_ADDRESS = 0x68
        self.PWR_MGMT_1 = 0x6B
        self.ACCEL_XOUT_H = 0x3B
        self.GYRO_XOUT_H = 0x43

        self.ax_offset = 0.0
        self.ay_offset = 0.0
        self.az_offset = 0.0

        self.load_calibration()

    def initialize(self):
        """Alias for init_sensor() to match other sensor classes."""
        self.init_sensor()

    def init_sensor(self):
        """Initialize the sensor if connected, else stay in simulation mode."""
        if self.SMBUS_AVAILABLE:
            try:
                self.bus.write_byte_data(self.MPU6050_ADDRESS, self.PWR_MGMT_1, 0)
                self.MPU_CONNECTED = True
                print("[INFO] MPU6050 initialized successfully.")
            except Exception as e:
                print(f"[WARN] MPU6050 not detected: {e}")
                self.MPU_CONNECTED = False
        else:
            print("[INFO] Skipping hardware initialization (simulation mode).")

    def read_accelerometer(self):
        """Read or simulate accelerometer data."""
        if self.SMBUS_AVAILABLE and self.MPU_CONNECTED:
            ax = self.read_raw_data(self.ACCEL_XOUT_H) / 16384.0
            ay = self.read_raw_data(self.ACCEL_XOUT_H + 2) / 16384.0
            az = self.read_raw_data(self.ACCEL_XOUT_H + 4) / 16384.0
        else:
            # Simulated data
            ax = random.uniform(-2, 2)
            ay = random.uniform(-2, 2)
            az = random.uniform(-2, 2)
        return ax, ay, az

    def calibrate_accelerometer(self, num_samples=100):
        """Calibrate accelerometer by averaging multiple readings."""
        ax_sum = ay_sum = az_sum = 0.0
        for _ in range(num_samples):
            ax, ay, az = self.read_accelerometer()
            ax_sum += ax
            ay_sum += ay
            az_sum += az
            time.sleep(0.01)

        self.ax_offset = ax_sum / num_samples
        self.ay_offset = ay_sum / num_samples
        self.az_offset = az_sum / num_samples

        print(f"[INFO] Calibration complete: ax={self.ax_offset:.2f}, ay={self.ay_offset:.2f}, az={self.az_offset:.2f}")

        self.save_calibration()  # Save the calibration data after calibration

    def get_calibrated_acceleration(self):
        """Return calibrated accelerometer readings."""
        ax, ay, az = self.read_accelerometer()
        return ax - self.ax_offset, ay - self.ay_offset, az - self.az_offset

    def read_raw_data(self, addr):
        """Read two bytes of data from the given address."""
        high = self.bus.read_byte_data(self.MPU6050_ADDRESS, addr)
        low = self.bus.read_byte_data(self.MPU6050_ADDRESS, addr + 1)
        value = (high << 8) | low
        # Convert to signed value
        if value > 32767:
            value -= 65536
        return value

    def save_calibration(self):
        """Save the calibration data to a file."""
        calibration_file = "mpu6050_calibration.txt"
        with open(calibration_file, 'w') as f:
            f.write(f"{self.ax_offset}\n")
            f.write(f"{self.ay_offset}\n")
            f.write(f"{self.az_offset}\n")
        print(f"[INFO] MPU6050 calibration saved: ax_offset={self.ax_offset}, ay_offset={self.ay_offset}, az_offset={self.az_offset}")

    def load_calibration(self):
        """Load calibration data from a file."""
        calibration_file = "mpu6050_calibration.txt"
        if os.path.exists(calibration_file):
            with open(calibration_file, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    self.ax_offset = float(lines[0].strip())
                    self.ay_offset = float(lines[1].strip())
                    self.az_offset = float(lines[2].strip())
                    print(f"[INFO] Loaded MPU6050 calibration: ax_offset={self.ax_offset}, ay_offset={self.ay_offset}, az_offset={self.az_offset}")
        else:
            print("[INFO] No MPU6050 calibration file found. Using default calibration.")
