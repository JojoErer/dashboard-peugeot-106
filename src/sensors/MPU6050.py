# mpu6050_sensor.py
import time
import random

class MPU6050:
    def __init__(self):
        """Initialize the MPU6050 sensor or enable simulation mode if unavailable."""
        self.SMBUS_AVAILABLE = False
        self.MPU_CONNECTED = False
        self.bus = None

        try:
            import smbus2
            self.bus = smbus2.SMBus(1)
            self.SMBUS_AVAILABLE = True
        except (ImportError, FileNotFoundError):
            print("[INFO] smbus not found. Running in simulation mode.")

        # MPU6050 register addresses
        self.MPU6050_ADDRESS = 0x68
        self.PWR_MGMT_1 = 0x6B
        self.ACCEL_XOUT_H = 0x3B
        self.GYRO_XOUT_H = 0x43

        self.ax_offset = 0.0
        self.ay_offset = 0.0
        self.az_offset = 0.0

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
            # data = self.bus.read_i2c_block_data(self.MPU6050_ADDRESS, self.ACCEL_XOUT_H, 6)
            ax = self.read_raw_data(self.ACCEL_XOUT_H) / 16384.0
            ay = self.read_raw_data(self.ACCEL_XOUT_H + 2) / 16384.0
            az = self.read_raw_data(self.ACCEL_XOUT_H + 4) / 16384.0
        else:
            # Simulated data
            ax = random.uniform(-0.5, 0.5)
            ay = random.uniform(-0.5, 0.5)
            az = random.uniform(0.8, 1.2)
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

    def get_calibrated_acceleration(self):
        """Return calibrated accelerometer readings."""
        ax, ay, az = self.read_accelerometer()
        return ax - self.ax_offset, ay - self.ay_offset, az - self.az_offset
    
    def read_raw_data(self, addr):
        # Read two bytes of data from the given address
        high = self.bus.read_byte_data(self.MPU6050_ADDRESS, addr)
        low = self.bus.read_byte_data(self.MPU6050_ADDRESS, addr+1)
        value = (high << 8) | low
        # Convert to signed value
        if value > 32767:
            value -= 65536
        return value
