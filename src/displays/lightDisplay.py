import tkinter as tk
from src.sensors.LDRLM393 import LightSensor

class LightDisplay:
    def __init__(self, light_sensor=None, test_mode=False):
        self.test_mode = test_mode
        self.light_sensor = light_sensor

        self.root = tk.Tk()
        self.root.title("Light Sensor Display")
        self.root.configure(bg="black")
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.label1 = tk.Label(self.root, text="", font=("Arial", 24), fg="white", bg="black")
        self.label1.pack(pady=20)
        self.label2 = tk.Label(self.root, text="", font=("Arial", 24), fg="white", bg="black")
        self.label2.pack(pady=20)

        self.update_display()

    def update_display(self):
        if self.test_mode:
            light1, light2 = 1, 0
        else:
            light1 = self.light_sensor.read_light_intensity(self.light_sensor.pin1)
            light2 = self.light_sensor.read_light_intensity(self.light_sensor.pin2)

        self.label1.config(text=f"Sensor 1: {'ON' if light1 else 'OFF'}")
        self.label2.config(text=f"Sensor 2: {'ON' if light2 else 'OFF'}")

        self.root.after(1000, self.update_display)  # refresh every second

    def run(self):
        self.root.mainloop()
