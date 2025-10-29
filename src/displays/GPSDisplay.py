import os
import math
from PIL import Image, ImageDraw, ImageTk


class OfflineMap:
    """
    Simple offline map viewer using QGIS XYZ or TMS tiles.
    Always shows an 800×800 map centered on the car.
    No hidden buffer.
    """

    def __init__(self, map_folder, zoom=14, tile_size=500, view_size=800, tms_mode=None):
        self.map_folder = map_folder
        self.zoom = zoom
        self.tile_size = tile_size
        self.view_size = view_size
        self.tms_mode = tms_mode if tms_mode is not None else self._detect_tms()

    # ---------- Coordinate math ----------
    def deg2num(self, lat, lon):
        """Convert lat/lon → tile X,Y indices."""
        lat_rad = math.radians(lat)
        n = 2.0 ** self.zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        if self.tms_mode:
            ytile = int((2 ** self.zoom - 1) - ytile)
        return xtile, ytile

    def latlon_to_pixel(self, lat, lon):
        """Convert lat/lon → global pixel coordinates."""
        lat_rad = math.radians(lat)
        n = 2.0 ** self.zoom
        x = (lon + 180.0) / 360.0 * n * self.tile_size
        y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n * self.tile_size
        if self.tms_mode:
            total_pix = (2 ** self.zoom) * self.tile_size
            y = total_pix - y
        return x, y

    def _detect_tms(self):
        """Check if Y-axis needs flipping (TMS)."""
        test_lat, test_lon = 52.0907, 5.1214
        xtile, ytile_xyz = self._calc_xyz_y(test_lat, test_lon)
        ytile_tms = (2 ** self.zoom - 1) - ytile_xyz
        path_xyz = os.path.join(self.map_folder, str(self.zoom), str(xtile), f"{ytile_xyz}.png")
        path_tms = os.path.join(self.map_folder, str(self.zoom), str(xtile), f"{ytile_tms}.png")
        if os.path.exists(path_tms) and not os.path.exists(path_xyz):
            return True
        return False

    def _calc_xyz_y(self, lat, lon):
        lat_rad = math.radians(lat)
        n = 2.0 ** self.zoom
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    # ---------- Main function ----------
    def render_map(self, lat, lon):
        """
        Generate an 800×800 map centered on the given lat/lon.
        Returns a PhotoImage ready for Tkinter.
        """
        global_x, global_y = self.latlon_to_pixel(lat, lon)
        min_x = global_x - self.view_size / 2
        min_y = global_y - self.view_size / 2
        max_x = global_x + self.view_size / 2
        max_y = global_y + self.view_size / 2

        # Determine which tiles are needed
        tile_x_start = int(min_x // self.tile_size)
        tile_x_end = int(max_x // self.tile_size)
        tile_y_start = int(min_y // self.tile_size)
        tile_y_end = int(max_y // self.tile_size)

        width_tiles = tile_x_end - tile_x_start + 1
        height_tiles = tile_y_end - tile_y_start + 1

        map_img = Image.new("RGBA", (width_tiles * self.tile_size, height_tiles * self.tile_size), (220, 220, 220, 255))

        # Stitch only required tiles
        for tx in range(tile_x_start, tile_x_end + 1):
            for ty in range(tile_y_start, tile_y_end + 1):
                tile_path = os.path.join(self.map_folder, str(self.zoom), str(tx), f"{ty}.png")
                if os.path.exists(tile_path):
                    tile = Image.open(tile_path).convert("RGBA")
                    px = (tx - tile_x_start) * self.tile_size
                    py = (ty - tile_y_start) * self.tile_size
                    map_img.paste(tile, (px, py))
                else:
                    # Gray placeholder if missing
                    placeholder = Image.new("RGBA", (self.tile_size, self.tile_size), (180, 180, 180, 255))
                    draw = ImageDraw.Draw(placeholder)
                    draw.text((10, 10), f"{tx},{ty}", fill="black")
                    px = (tx - tile_x_start) * self.tile_size
                    py = (ty - tile_y_start) * self.tile_size
                    map_img.paste(placeholder, (px, py))

        # Crop to exactly 800×800 centered on current position
        offset_x = int(global_x - tile_x_start * self.tile_size - self.view_size / 2)
        offset_y = int(global_y - tile_y_start * self.tile_size - self.view_size / 2)

        cropped = map_img.crop((offset_x, offset_y, offset_x + self.view_size, offset_y + self.view_size))

        # Draw car marker in the center
        draw = ImageDraw.Draw(cropped)
        cx, cy = self.view_size // 2, self.view_size // 2
        draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill="red", outline="white", width=2)

        return ImageTk.PhotoImage(cropped)
