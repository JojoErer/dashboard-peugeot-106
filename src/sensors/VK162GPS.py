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

        # Last known GPS data
        self._last_data = {
            'latitude': None,
            'longitude': None,
            'speed': 0.0,
            'timestamp': None,
            'fix_status': 0,
            'fix_quality': "No Fix",
            'satellites': 0,           
            'satellites_visible': 0, 
            'hdop': None
        }

        # Auto-detect GPS
        if not port and not test_mode:
            ports = glob.glob('/dev/ttyACM*')
            if ports:
                self.port = ports[0]
                print(f"[INFO] Found VK-162 GPS on {self.port}")
            else:
                print("[INFO] No GPS found → test mode")
                self.test_mode = True

        if not self.test_mode and self.port:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=0)
                print(f"[INFO] GPS opened on {self.port}")
            except Exception as e:
                print(f"[ERROR] Failed to open GPS: {e}")
                self.test_mode = True

        print("[INFO] Initializing GPS (waiting for data)...")
        start = time.time()
        while time.time() - start < 2.0:
            if self.ser and self.ser.in_waiting:
                print("[INFO] GPS is responding")
                return
            time.sleep(0.1)

        print("[WARN] No GPS data received, switching to test mode")
        self.test_mode = True

    # =====================================================
    # ================= NMEA PARSING ======================
    # =====================================================
    def parse_nmea_sentence(self, sentence):
        data = {}

        if '*' in sentence:
            sentence = sentence.split('*')[0]

        parts = sentence.split(',')

        try:
            # ---------- GGA (fix + satellites used) ----------
            if parts[0] == "$GPGGA":
                fix = int(parts[6]) if parts[6].isdigit() else 0
                data['fix_status'] = fix

                fix_map = {
                    0: "No Fix",
                    1: "GPS Fix",
                    2: "DGPS Fix"
                }
                data['fix_quality'] = fix_map.get(fix, "Unknown")

                data['satellites'] = int(parts[7]) if parts[7].isdigit() else 0
                data['hdop'] = float(parts[8]) if parts[8] else None

            # ---------- GSV (satellites visible) ----------
            elif parts[0] == "$GPGSV":
                if parts[3].isdigit():
                    data['satellites_visible'] = int(parts[3])

            # ---------- RMC (position + speed) ----------
            elif parts[0] == "$GPRMC" and parts[2] == 'A':
                utc_time = parts[1]
                utc_date = parts[9]

                if len(utc_time) >= 6 and len(utc_date) == 6:
                    dt = datetime(
                        2000 + int(utc_date[4:6]),
                        int(utc_date[2:4]),
                        int(utc_date[0:2]),
                        int(utc_time[0:2]),
                        int(utc_time[2:4]),
                        int(utc_time[4:6]),
                        tzinfo=timezone.utc
                    )
                    data['timestamp'] = dt.astimezone(
                        ZoneInfo("Europe/Amsterdam")
                    ).strftime("%H:%M")

                if parts[7]:
                    data['speed'] = float(parts[7]) * 1.852

                lat_raw = float(parts[3])
                lon_raw = float(parts[5])

                lat = int(lat_raw / 100) + (lat_raw % 100) / 60.0
                lon = int(lon_raw / 100) + (lon_raw % 100) / 60.0

                if parts[4] == 'S':
                    lat = -lat
                if parts[6] == 'W':
                    lon = -lon

                data['latitude'] = lat
                data['longitude'] = lon

        except Exception:
            pass

        return data

    # =====================================================
    # ================= MAIN UPDATE =======================
    # =====================================================
    def get_data(self):
        if self.test_mode:
            self._last_data = {
                'latitude': 52.1070 + random.uniform(-0.002, 0.002),
                'longitude': 5.1214 + random.uniform(-0.002, 0.002),
                'speed': random.uniform(0, 120),
                'timestamp': datetime.now().strftime('%H:%M'),
                'fix_status': 1,
                'fix_quality': "GPS Fix",
                'satellites': 8,
                'satellites_visible': 12,
                'hdop': 0.9
            }
            return self._last_data

        start = time.time()
        while time.time() - start < 0.05:
            if not self.ser or not self.ser.in_waiting:
                break

            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if not line.startswith('$'):
                    continue

                parsed = self.parse_nmea_sentence(line)
                for key, value in parsed.items():
                    if value is not None:
                        self._last_data[key] = value

            except Exception:
                break

        return self._last_data

    # =====================================================
    # ================= CLEANUP ===========================
    # =====================================================
    def close(self):
        if self.ser:
            self.ser.close()
            self.ser = None