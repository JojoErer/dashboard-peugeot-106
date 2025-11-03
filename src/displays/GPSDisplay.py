import sys
import os
import math
import itertools
import random
from datetime import datetime

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QPainterPath, QLinearGradient

# --------------------- OfflineMap ---------------------
class OfflineMap:
    def __init__(self, map_folder, zoom=14, tile_size=500, view_size=800):
        self.map_folder = map_folder
        self.zoom = zoom
        self.tile_size = tile_size
        self.view_size = view_size

    def latlon_to_pixel(self, lat, lon):
        lat_rad = math.radians(lat)
        n = 2.0 ** self.zoom
        x = (lon + 180.0) / 360.0 * n * self.tile_size
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n * self.tile_size
        return x, y

    def render_map(self, lat, lon):
        global_x, global_y = self.latlon_to_pixel(lat, lon)
        min_x = global_x - self.view_size / 2
        min_y = global_y - self.view_size / 2
        max_x = global_x + self.view_size / 2
        max_y = global_y + self.view_size / 2

        tile_x_start = int(min_x // self.tile_size)
        tile_x_end = int(max_x // self.tile_size)
        tile_y_start = int(min_y // self.tile_size)
        tile_y_end = int(max_y // self.tile_size)

        width_tiles = tile_x_end - tile_x_start + 1
        height_tiles = tile_y_end - tile_y_start + 1

        img = QImage(width_tiles * self.tile_size, height_tiles * self.tile_size, QImage.Format_RGBA8888)
        img.fill(QColor(220, 220, 220, 255))
        painter = QPainter(img)

        for tx in range(tile_x_start, tile_x_end + 1):
            for ty in range(tile_y_start, tile_y_end + 1):
                tile_path = os.path.join(self.map_folder, str(self.zoom), str(tx), f"{ty}.png")
                px = (tx - tile_x_start) * self.tile_size
                py = (ty - tile_y_start) * self.tile_size
                if os.path.exists(tile_path):
                    tile_img = QImage(tile_path).convertToFormat(QImage.Format_RGBA8888)
                    painter.drawImage(px, py, tile_img)
                else:
                    placeholder = QImage(self.tile_size, self.tile_size, QImage.Format_RGBA8888)
                    placeholder.fill(QColor(180, 180, 180, 255))
                    painter.drawImage(px, py, placeholder)

        painter.end()

        offset_x = int(global_x - tile_x_start * self.tile_size - self.view_size / 2)
        offset_y = int(global_y - tile_y_start * self.tile_size - self.view_size / 2)
        cropped = img.copy(offset_x, offset_y, self.view_size, self.view_size)

        return cropped

# --------------------- GPSMapWidget ---------------------
class GPSMapWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- Fullscreen & borderless ---
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove borders and title bar
        self.showFullScreen()  # Show fullscreen

        # Get screen size dynamically
        screen_geometry = QApplication.primaryScreen().geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        self.radius = min(self.screen_width, self.screen_height) // 2

        self.map_folder = "lib/mapNL"
        self.map_viewer = OfflineMap(self.map_folder, view_size=self.radius*2)  # Map size matches circle diameter

        # Demo GPS points
        self.gps_points = [
            (52.0907, 5.1214),
            (52.0910, 5.1225),
            (52.0915, 5.1238),
            (52.0920, 5.1250),
            (52.0923, 5.1262),
            (52.0927, 5.1275),
            (52.0931, 5.1288),
        ]
        self.gps_cycle = itertools.cycle(self.gps_points)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Precompute bump path
        self.bump_width = 300
        self.bump_height = 150
        self.bump_path = QPainterPath()
        w, h = self.bump_width, self.bump_height
        self.bump_path.moveTo(-w/2, 0)
        self.bump_path.cubicTo(-w/4, -h, w/4, -h, w/2, 0)
        self.bump_path.closeSubpath()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000)

        self.update_position()

    def draw_edge_bump(self, painter, center_x, center_y, angle_deg, radius, color, text):
        angle_rad = math.radians(angle_deg)
        edge_x = center_x + (radius + 5) * math.cos(angle_rad)
        edge_y = center_y - (radius + 5) * math.sin(angle_rad)

        painter.save()
        painter.translate(edge_x, edge_y)
        painter.rotate(-angle_deg - 90)

        gradient = QLinearGradient(0, -self.bump_height/4, 0, -self.bump_height)
        gradient.setColorAt(0, color)
        gradient.setColorAt(0.3, QColor(0, 0, 0, 200))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPath(self.bump_path)

        painter.rotate(angle_deg + 90)
        font = QFont("Arial", 20, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("white"))
        text_rect = QRectF(-self.bump_width/2, -self.bump_height*0.15, self.bump_width, self.bump_height)
        painter.drawText(text_rect, Qt.AlignCenter, text)

        painter.restore()

    def update_position(self):
        lat, lon = next(self.gps_cycle)
        map_img = self.map_viewer.render_map(lat, lon)

        final_img = QImage(self.screen_width, self.screen_height, QImage.Format_RGBA8888)
        final_img.fill(QColor("black"))

        painter = QPainter(final_img)
        painter.setRenderHint(QPainter.Antialiasing)

        # --- Fullscreen circular map ---
        path = QPainterPath()
        path.addEllipse(self.center_x - self.radius, self.center_y - self.radius, self.radius*2, self.radius*2)
        painter.setClipPath(path)
        painter.drawImage(self.center_x - self.radius, self.center_y - self.radius, map_img)
        painter.setClipping(False)

        # --- Red car dot ---
        dot_radius = 12
        painter.setBrush(QColor("red"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.center_x - dot_radius//2, self.center_y - dot_radius//2, dot_radius, dot_radius)

        # --- Draw bumps ---
        velocity = random.randint(0, 120)
        now = datetime.now().strftime("%H:%M")
        self.draw_edge_bump(painter, self.center_x, self.center_y, 60, self.radius, QColor("black"), f"{velocity} km/h")
        self.draw_edge_bump(painter, self.center_x, self.center_y, 120, self.radius, QColor("black"), now)

        painter.end()
        self.label.setPixmap(QPixmap.fromImage(final_img))
