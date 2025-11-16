import serial
import time
import random
import glob
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class VK162GPS:
    def __init__(self, port=None, baudrate=9600, test_mode=False):
        self.port = port
        self.baudrate = baudrate
        self.test_mode = test_mode
        self.ser = None

        # Store last known GPS data
        self._last_data = {
            'latitude': None,
            'longitude': None,
            'speed': 0.0,
            'timestamp': None,
            'fix_status': 0,
            'satellites': 0,
            'hdop': None
        }

        # Auto-detect VK-162 (USB)
        if not port and not test_mode:
            possible_ports = glob.glob('/dev/ttyACM0*')
            if possible_ports:
                self.port = possible_ports[0]
                print(f"[INFO] Found VK-162 GPS on {self.port}")
            else:
                print("[INFO] No GPS device found. Switching to test mode.")
                self.test_mode = True

        if not self.test_mode and self.port:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
                print(f"[INFO] Connected to GPS on {self.port} ({self.baudrate} baud)")
            except Exception as e:
                print(f"[INFO] Could not open {self.port}: {e}")
                self.test_mode = True

    def initialize(self):
        """GPS is considered initialized even without satellite lock."""
        if self.test_mode:
            print("[INFO] Running in GPS test mode (simulated data).")
            return True

        print("[INFO] Initializing GPS...")
        # Just check if we receive ANY NMEA data
        for _ in range(10):
            line = self.read_gps_data()
            if line:
                print("[INFO] GPS is responding (may or may not have fix).")
                return True
            time.sleep(1)

        print("[INFO] No NMEA data received. Switching to test mode.")
        self.test_mode = True
        return True

    def read_gps_data(self):
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
        """Parse NMEA and return usable data."""
        gps_data = {
            'latitude': None,
            'longitude': None,
            'speed': None,
            'timestamp': None,
            'fix_status': None,
            'satellites': None,
            'hdop': None
        }

        # Strip checksum
        if '*' in nmea_sentence:
            nmea_sentence = nmea_sentence.split('*')[0]

        parts = nmea_sentence.split(',')
        if len(parts) < 3:
            return gps_data

        try:
            # GGA sentence → fix quality, satellites, hdop, lat/lon
            if parts[0] == "$GPGGA":
                gps_data['fix_status'] = int(parts[6]) if parts[6].isdigit() else 0
                gps_data['satellites'] = int(parts[7]) if parts[7].isdigit() else 0
                gps_data['hdop'] = float(parts[8]) if parts[8] else None

                if gps_data['fix_status'] > 0 and parts[2] and parts[4]:
                    lat_raw = float(parts[2])
                    lat_deg = int(lat_raw / 100)
                    lat_min = lat_raw - lat_deg * 100
                    latitude = lat_deg + lat_min / 60.0
                    if parts[3] == 'S':
                        latitude = -latitude

                    lon_raw = float(parts[4])
                    lon_deg = int(lon_raw / 100)
                    lon_min = lon_raw - lon_deg * 100
                    longitude = lon_deg + lon_min / 60.0
                    if parts[5] == 'W':
                        longitude = -longitude

                    gps_data['latitude'] = latitude
                    gps_data['longitude'] = longitude

            # RMC sentence → UTC time + speed + lat/lon
            elif parts[0] == "$GPRMC":
                status = parts[2]  # A = valid, V = void
                utc_time = parts[1]
                utc_date = parts[9]

                if len(utc_time) >= 6 and len(utc_date) == 6:
                    day = int(utc_date[0:2])
                    month = int(utc_date[2:4])
                    year = 2000 + int(utc_date[4:6])  # convert YY to 20YY

                    hours = int(utc_time[0:2])
                    minutes = int(utc_time[2:4])
                    seconds = int(utc_time[4:6])

                    # Build a precise UTC datetime from GPS
                    utc_dt = datetime(year, month, day, hours, minutes, seconds, tzinfo=timezone.utc)

                    # Convert to Dutch time (DST aware)
                    dutch_time = utc_dt.astimezone(ZoneInfo("Europe/Amsterdam"))

                    gps_data['timestamp'] = dutch_time.strftime("%H:%M")

                # Speed in knots → km/h
                if parts[7]:
                    try:
                        gps_data['speed'] = float(parts[7]) * 1.852
                    except:
                        gps_data['speed'] = 0.0

                # Only update lat/lon if valid fix
                if status == 'A' and parts[3] and parts[5]:
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
        if self.test_mode:
            self._last_data = {
                'latitude': 52.1070 + random.uniform(-0.005, 0.005),
                'longitude': 5.1214 + random.uniform(-0.005, 0.005),
                'speed': random.uniform(110, 120),
                'timestamp': datetime.now().strftime('%H:%M'),
                'fix_status': 1,
                'satellites': 8,
                'hdop': 0.9
            }
            return self._last_data

        sentence = self.read_gps_data()
        if sentence:
            parsed = self.parse_nmea_sentence(sentence)
            # Update last known data only if values are not None
            for key, value in parsed.items():
                if value is not None:
                    self._last_data[key] = value

        # Always return last known data
        return self._last_data

    def close(self):
        if self.ser:
            self.ser.close()
            print("[INFO] GPS connection closed.")
