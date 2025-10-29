import serial
import time
from datetime import datetime

class GPSReader:
    def __init__(self, port='/dev/serial0', baudrate=9600):
        """
        Initialize the GPS reader with a given serial port and baudrate.
        :param port: Serial port where the GPS is connected (default is /dev/serial0).
        :param baudrate: Baud rate of the GPS module (default is 9600).
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate, timeout=1)
    
    def initialize(self):
        """
        Initialize the GPS sensor by checking if it is sending valid data.
        :return: True if the GPS is working and valid data is received, False otherwise.
        """
        print("Initializing GPS...")
        try:
            # Attempt to read the first few sentences and check for valid data
            for _ in range(5):  # Try to read 5 sentences to ensure connection
                nmea_sentence = self.read_gps_data()
                if nmea_sentence:
                    print(f"Received NMEA sentence: {nmea_sentence}")
                    gps_data = self.parse_nmea_sentence(nmea_sentence)
                    if gps_data['latitude'] is not None and gps_data['longitude'] is not None:
                        print("GPS initialized successfully.")
                        return True  # GPS is working, valid position data received
                time.sleep(1)
            
            print("Failed to initialize GPS: No valid data received.")
            return False
        
        except Exception as e:
            print(f"Error initializing GPS: {e}")
            return False

    def read_gps_data(self):
        """
        Reads data from the GPS module and returns it as a string.
        :return: Raw GPS sentence or None if no data is available.
        """
        try:
            # Read a line of data from the GPS module
            data = self.ser.readline().decode('utf-8').strip()
            return data
        except Exception as e:
            print(f"Error reading data: {e}")
            return None
    
    def parse_nmea_sentence(self, nmea_sentence):
        """
        Parses an NMEA sentence and extracts GPS information (lat, lon, speed, and time).
        :param nmea_sentence: The raw NMEA sentence to be parsed.
        :return: A dictionary with latitude, longitude, speed, and time.
        """
        gps_data = {
            'latitude': None,
            'longitude': None,
            'speed': None,
            'timestamp': None
        }
        
        # Parse $GPGGA (Position data)
        if nmea_sentence.startswith('$GPGGA'):
            try:
                parts = nmea_sentence.split(',')
                if parts[2] != '' and parts[4] != '':
                    lat = float(parts[2]) / 100.0
                    lat = int(lat) + (lat - int(lat)) * 100.0 / 60.0
                    if parts[3] == 'S':
                        lat = -lat

                    lon = float(parts[4]) / 100.0
                    lon = int(lon) + (lon - int(lon)) * 100.0 / 60.0
                    if parts[5] == 'W':
                        lon = -lon

                    gps_data['latitude'] = lat
                    gps_data['longitude'] = lon
                else:
                    print("GPS fix is not available.")
            except Exception as e:
                print(f"Error parsing $GPGGA: {e}")
        
        # Parse $GPRMC (Speed and Time data)
        if nmea_sentence.startswith('$GPRMC'):
            try:
                parts = nmea_sentence.split(',')
                # Time (UTC)
                utc_time = parts[1]
                if len(utc_time) >= 6:
                    # Format time: HHMMSS
                    timestamp = datetime.strptime(utc_time, '%H%M%S')
                    gps_data['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                # Speed in knots (convert to km/h by multiplying by 1.852)
                speed_knots = parts[7]
                if speed_knots != '' and speed_knots != '0.0':
                    gps_data['speed'] = float(speed_knots) * 1.852  # Speed in km/h
                else:
                    gps_data['speed'] = 0.0
            except Exception as e:
                print(f"Error parsing $GPRMC: {e}")

        return gps_data
    
    def close(self):
        """Close the serial connection."""
        self.ser.close()

# Example usage
if __name__ == "__main__":
    gps_reader = GPSReader()

    # Initialize GPS
    if gps_reader.initialize():
        try:
            while True:
                nmea_sentence = gps_reader.read_gps_data()
                if nmea_sentence:
                    print(f"Received NMEA sentence: {nmea_sentence}")
                    gps_data = gps_reader.parse_nmea_sentence(nmea_sentence)
                    
                    if gps_data['latitude'] is not None and gps_data['longitude'] is not None:
                        print(f"Latitude: {gps_data['latitude']}, Longitude: {gps_data['longitude']}")
                    
                    if gps_data['speed'] is not None:
                        print(f"Speed: {gps_data['speed']} km/h")
                    
                    if gps_data['timestamp'] is not None:
                        print(f"Time (UTC): {gps_data['timestamp']}")
                    
                    print("-------------------------")
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting GPS Reader...")
        finally:
            gps_reader.close()
    else:
        print("GPS initialization failed. Exiting.")
