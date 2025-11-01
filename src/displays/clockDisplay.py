import tkinter as tk
import time
import math
import sys

class Clock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fullscreen Analog Clock")

        # === Cross-platform fullscreen setup ===
        if sys.platform.startswith("linux"):
            try:
                self.root.attributes("-zoomed", False)
            except tk.TclError:
                pass
            self.root.attributes("-fullscreen", False)
        else:
            self.root.attributes("-fullscreen", False)

        # Remove window borders (kiosk mode)
        self.root.overrideredirect(True)

        # Fallback: manually fill the screen
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+0+0")

        # Background and exit key
        self.root.configure(bg="black")
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        # ========================================

        # Create canvas that auto-fills the screen
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # State
        self.light_parameter = 0
        self.update_clock()

    def get_light_color(self):
        return "white" if self.light_parameter == 0 else "yellow"

    def draw_clock(self):
        """Draws the analog clock centered and scaled to the current screen."""
        # --- CHANGED: only delete clock graphics, not overlays ---
        self.canvas.delete("clock_elements")

        light = self.get_light_color()

        # Get current canvas size
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        cx, cy = width // 2, height // 2
        radius = min(width, height) // 2 - 1

        # ---- Clock Face ----
        self.canvas.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            outline=light, width=5, tags="clock_elements"  # <-- CHANGED
        )

        # ---- Minute & Hour Marks ----
        for i in range(60):
            angle = i * math.pi / 30
            inner = radius - (30 if i % 5 == 0 else 15)
            x1 = cx + math.sin(angle) * inner
            y1 = cy - math.cos(angle) * inner
            x2 = cx + math.sin(angle) * radius
            y2 = cy - math.cos(angle) * radius
            width_line = 5 if i % 5 == 0 else 2
            self.canvas.create_line(
                x1, y1, x2, y2, fill=light, width=width_line, tags="clock_elements"  # <-- CHANGED
            )

        # ---- Hour Numbers ----
        for i in range(1, 13):
            angle = i * math.pi / 6
            x = cx + math.sin(angle) * (radius - 70)
            y = cy - math.cos(angle) * (radius - 70)
            self.canvas.create_text(
                x, y, text=str(i),
                font=("Arial", radius // 10, "bold"),
                fill=light, tags="clock_elements"  # <-- CHANGED
            )

        # ---- Time Hands ----
        now = time.localtime()
        hour_ang = (now.tm_hour % 12 + now.tm_min / 60) * math.pi / 6
        min_ang = now.tm_min * math.pi / 30

        # Hour hand
        self.canvas.create_line(
            cx, cy,
            cx + math.sin(hour_ang) * (radius * 0.55),
            cy - math.cos(hour_ang) * (radius * 0.55),
            width=6, fill=light, tags="clock_elements"  # <-- CHANGED
        )
        self.canvas.create_line(
            cx, cy,
            cx - math.sin(hour_ang) * (radius * 0.1),
            cy + math.cos(hour_ang) * (radius * 0.1),
            width=6, fill=light, tags="clock_elements"  # <-- CHANGED
        )

        # ---- Center Cap ----
        self.canvas.create_oval(
            cx - 30, cy - 30, cx + 30, cy + 30,
            fill="black", tags="clock_elements"  # <-- CHANGED
        )

        # Minute hand
        self.canvas.create_line(
            cx, cy,
            cx + math.sin(min_ang) * (radius * 0.65),
            cy - math.cos(min_ang) * (radius * 0.65),
            width=4, fill=light, tags="clock_elements"  # <-- CHANGED
        )
        self.canvas.create_line(
            cx, cy,
            cx - math.sin(min_ang) * (radius * 0.1),
            cy + math.cos(min_ang) * (radius * 0.1),
            width=4, fill=light, tags="clock_elements"  # <-- CHANGED
        )

        # ---- Label ----
        self.canvas.create_text(
            cx, cy + radius * 0.4,
            text="Quartz", font=("Arial", radius // 15),
            fill=light, tags="clock_elements"  # <-- CHANGED
        )

    def update_clock(self):
        self.draw_clock()
        self.root.after(1000, self.update_clock)

    def run(self):
        self.root.mainloop()
