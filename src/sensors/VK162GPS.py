import serial
import time
import random
import glob
from datetime import datetime

class VK162GPS:
    def __init__(self, port=None, baudrate=9600, test_mode=False):
        """
        VK-162 GPS Reader
        Automatically detects /dev/ttyUSB* ports if no port is provided.
        :param test_mode: If True, generates simulated GPS data.
        """
        self.port = port
        self.baudrate = baudrate
        self.test_mode = test_mode
        self.ser = None

        # Auto-detect VK-162 (USB) if not specified
        if not port and not test_mode:
            possible_ports = glob.glob('/dev/ttyUSB*')
            if possible_ports:
                self.port = possible_ports[0]
                print(f"✅ Found VK-162 GPS on {self.port}")
            else:
                print("⚠️ No GPS device found. Switching to test mode.")
                self.test_mode = True

        if not self.test_mode and self.port:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                print(f"📡 Connected to GPS on {self.port} ({self.baudrate} baud)")
            except Exception as e:
                print(f"❌ Could not open {self.port}: {e}")
                self.test_mode = True

    def initialize(self):
        """Check if GPS is working, or fallback to test mode."""
        if self.test_mode:
            print("🧪 Running in GPS test mode (simulated data).")
            return True

        print("Initializing GPS (waiting for valid NMEA sentences)...")
        try:
            for _ in range(10):
                nmea_sentence = self.read_gps_data()
                if nmea_sentence and ('$GPGGA' in nmea_sentence or '$GPRMC' in nmea_sentence):
                    gps_data = self.parse_nmea_sentence(nmea_sentence)
                    if gps_data['latitude'] and gps_data['longitude']:
                        print("✅ VK-162 GPS initialized successfully.")
                        return True
                time.sleep(1)
            print("❌ No valid GPS data received. Switching to test mode.")
            self.test_mode = True
            return True
        except Exception as e:
            print(f"Error initializing GPS: {e}")
            self.test_mode = True
            return True

    def read_gps_data(self):
        """Read one line of NMEA data from the GPS device."""
        if self.test_mode:
            return None
        try:
            data = self.ser.readline().decode('ascii', errors='ignore').strip()
            if data.startswith('$'):
                return data
        except Exception as e:
            print(f"Error reading GPS data: {e}")
        return None

    def parse_nmea_sentence(self, nmea_sentence):
        """Parse NMEA $GPGGA and $GPRMC sentences."""
        gps_data = {'latitude': None, 'longitude': None, 'speed': None, 'timestamp': None}

        # Clean checksum part if exists
        if '*' in nmea_sentence:
            nmea_sentence = nmea_sentence.split('*')[0]

        parts = nmea_sentence.split(',')
        if len(parts) < 6:
            return gps_data

        try:
            if parts[0] == "$GPGGA" and parts[2] and parts[4]:
                # Latitude
                lat_raw = float(parts[2])
                lat_deg = int(lat_raw / 100)
                lat_min = lat_raw - lat_deg * 100
                latitude = lat_deg + lat_min / 60.0
                if parts[3] == 'S':
                    latitude = -latitude

                # Longitude
                lon_raw = float(parts[4])
                lon_deg = int(lon_raw / 100)
                lon_min = lon_raw - lon_deg * 100
                longitude = lon_deg + lon_min / 60.0
                if parts[5] == 'W':
                    longitude = -longitude

                gps_data['latitude'] = latitude
                gps_data['longitude'] = longitude

            elif parts[0] == "$GPRMC":
                # UTC time
                utc_time = parts[1]
                if len(utc_time) >= 6:
                    timestamp = datetime.strptime(utc_time[:4], '%H%M')
                    gps_data['timestamp'] = timestamp.strftime('%H:%M')

                # Speed in knots -> km/h
                if len(parts) > 7 and parts[7]:
                    gps_data['speed'] = float(parts[7]) * 1.852

                # Latitude and Longitude
                if len(parts) > 5 and parts[3] and parts[5]:
                    lat_raw = float(parts[3])
                    lat_deg = int(lat_raw / 100)
                    lat_min = lat_raw - lat_deg * 100
                    latitude = lat_deg + lat_min / 60.0
                    if parts[4] == 'S':
                        latitude = -latitude

                    lon_raw = float(parts[5])
                    lon_deg = int(lon_raw / 100)
                    lon_min = lon_raw - lon_deg * 100
                    longitude = lon_deg + lon_min / 60.0
                    if parts[6] == 'W':
                        longitude = -longitude

                    gps_data['latitude'] = latitude
                    gps_data['longitude'] = longitude

        except Exception as e:
            print(f"Error parsing NMEA sentence: {e}")

        return gps_data

    def get_data(self):
        """Returns the most recent GPS fix (real or simulated)."""
        if self.test_mode:
            # Simulated data
            return {
                'latitude': 52.1070 + random.uniform(-0.005, 0.005),
                'longitude': 5.1214 + random.uniform(-0.005, 0.005),
                'speed': random.uniform(110, 120),
                'timestamp': datetime.now().strftime('%H:%M')
            }

        nmea_sentence = self.read_gps_data()
        if nmea_sentence:
            gps_data = self.parse_nmea_sentence(nmea_sentence)
            if gps_data['latitude'] and gps_data['longitude']:
                return gps_data

        # fallback if invalid or no fix
        return {
            'latitude': None,
            'longitude': None,
            'speed': 0.0,
            'timestamp': datetime.utcnow().strftime('%H:%M:%S')
        }

    def close(self):
        if self.ser:
            self.ser.close()
            print("🔌 GPS connection closed.")