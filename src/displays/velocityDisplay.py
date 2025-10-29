import time
from src.sensors.NEO6M import GPSReader
from displays.clockDisplay import Clock

class VelocityOverlay:
    def __init__(self, clock):
        self.clock = clock
        self.gps_reader = GPSReader()  # Initialize GPS reader
        if not self.gps_reader.initialize():
            print("GPS initialization failed. Speed overlay will not work.")
            self.speed = 0.0
        self.speed = 0.0  # Initial speed
        self.update_speed()

    def update_speed(self):
        """
        Update the GPS speed and overlay it on the clock.
        This method will be called periodically to update the speed on the display.
        """
        gps_data = self.gps_reader.read_gps_data()
        if gps_data:
            parsed_data = self.gps_reader.parse_nmea_sentence(gps_data)
            self.speed = parsed_data['speed'] if parsed_data['speed'] is not None else 0.0
        
        # Overlay the speed on the clock
        self.overlay_speed(self.speed)

    def overlay_speed(self, speed):
        """Overlay the GPS speed onto the clock."""
        speed_text = f"Speed: {speed:.2f} km/h"
        self.clock.canvas.create_text(self.clock.origin_x, self.clock.origin_y + 250,
                                      text=speed_text, font=("Arial", 20), fill="white")

    def start_speed_updates(self):
        """
        Update the speed every second.
        This method triggers `update_speed` every 1000 ms (1 second).
        """
        self.update_speed()
        self.clock.root.after(1000, self.start_speed_updates)