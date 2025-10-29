import os
import time
import pygame
import numpy as np
from collections import deque
import pywavefront
import io

class CarDisplay:
    def __init__(
        self,
        obj_file=None,
        update_rate=10,
        ax_offset=0,
        ay_offset=0,
        smoothing=0.2,
        show_graph=True,  # default to True to see graph
    ):
        pygame.init()
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption("2D Car Tilt Display")

        # Parameters
        self.update_period = 1 / update_rate
        self.ax_offset = ax_offset
        self.ay_offset = ay_offset
        self.smoothing = smoothing
        self.show_graph = show_graph
        self.graph_history = deque(maxlen=update_rate*10)
        self.graph_times = deque(maxlen=update_rate*10)

        # Car state
        self.center_x = self.width // 2
        self.center_y = self.height // 2 - 100  # move car up a bit to fit graph below
        self.pitch = 0.0  # front/back tilt
        self.roll = 0.0   # left/right tilt
        self.target_pitch = 0.0
        self.target_roll = 0.0
        self.ax = 0
        self.ay = 0
        self.az = 0
        self.car_scale = 1.5  # make car bigger

        # Load OBJ or fallback
        self.model_surface = self._load_obj_topdown(obj_file) if obj_file else None
        if self.model_surface is None:
            print("[WARN] No valid OBJ found. Using fallback car shape.")
            self.model_surface = self._create_fallback_car_surface()

        # Scale up the car
        w, h = self.model_surface.get_size()
        self.model_surface = pygame.transform.smoothscale(
            self.model_surface, (int(w*self.car_scale), int(h*self.car_scale))
        )

        # Fonts
        self.font = pygame.font.SysFont("consolas", 40, bold=True)
        self.graph_font = pygame.font.SysFont("consolas", 20)

    # --------------------------
    # OBJ handling
    # --------------------------
    def _load_obj_topdown(self, path):
        if not os.path.exists(path):
            return None
        try:
            # Load OBJ using pywavefront directly
            scene = pywavefront.Wavefront(path, collect_faces=True)
            verts = np.array(scene.vertices)
            if verts.size == 0:
                return None

            xs, zs = verts[:, 0], verts[:, 2]  # top-down: X-Z plane
            min_x, max_x = xs.min(), xs.max()
            min_z, max_z = zs.min(), zs.max()
            scale = 150 / max(max_x - min_x, max_z - min_z)

            # Project vertices to 2D
            x_scaled = (xs - (min_x + max_x)/2) * scale
            z_scaled = (zs - (min_z + max_z)/2) * scale
            points2d = np.column_stack((x_scaled, -z_scaled))  # flip Z

            size = int(max(np.max(x_scaled) - np.min(x_scaled), np.max(z_scaled) - np.min(z_scaled)) + 200)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)

            # Draw faces
            for name, mesh in scene.meshes.items():
                color = (90, 18, 18)
                for face in mesh.faces:
                    pts = [(points2d[i][0]+size//2, points2d[i][1]+size//2) for i in face]
                    pygame.draw.polygon(surf, color, pts)

            print(f"[INFO] Loaded OBJ '{path}' as top-down projection.")
            return surf

        except Exception as e:
            print(f"[WARN] OBJ load failed: {e}")
            return None


    def _create_fallback_car_surface(self):
        w, h = 120, 200
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (50, 200, 255), (0, 0, w, h), border_radius=20)
        pygame.draw.rect(surf, (80, 120, 255), (10, 20, w-20, h-40), border_radius=10)
        pygame.draw.rect(surf, (255, 100, 100), (0, 0, w, 30), border_radius=10)
        return surf

    # --------------------------
    # Main loop
    # --------------------------
    def run(self, read_accelerometer_data):
        print("[INFO] Starting 2D tilt display... Press ESC to exit.")
        clock = pygame.time.Clock()
        last_update = time.time()
        running = True
        base_car = self.model_surface

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False

            # --- Sensor update ---
            now = time.time()
            if now - last_update >= self.update_period:
                last_update = now
                self.ax, self.ay, self.az = read_accelerometer_data()
                ax = self.ax - self.ax_offset
                ay = self.ay - self.ay_offset
                self.target_pitch = np.clip(ax*40, -30, 30)
                self.target_roll = np.clip(ay*40, -30, 30)

                if self.show_graph:
                    self.graph_history.append((ax, ay))
                    self.graph_times.append(now)

            # --- Smooth transitions ---
            self.pitch += self.smoothing * (self.target_pitch - self.pitch)
            self.roll += self.smoothing * (self.target_roll - self.roll)

           # --- Draw scene ---
            self.screen.fill((15, 15, 25))

            # Make car slightly bigger
            scale_factor = 1.5
            car_w, car_h = base_car.get_size()
            base_car_scaled = pygame.transform.smoothscale(base_car, (int(car_w*scale_factor), int(car_h*scale_factor)))

            rotated = pygame.transform.rotate(base_car_scaled, self.roll)
            rect = rotated.get_rect(center=(self.center_x, self.center_y))
            self.screen.blit(rotated, rect.topleft)

            # --- Draw Acceleratie x (left) ---
            lines_ax = [
                "Acceleratie x:",
                f"{self.ax:+.2f}"
            ]
            x_ax = self.center_x - base_car_scaled.get_width()//2
            y_start = self.center_y - 20
            for i, line in enumerate(lines_ax):
                surf = self.font.render(line, True, (255, 255, 255))
                rect_text = surf.get_rect(center=(x_ax, y_start + i * self.font.get_linesize()))
                self.screen.blit(surf, rect_text)

            # --- Draw Acceleratie y (right) ---
            lines_ay = [
                "Acceleratie y:",
                f"{self.ay:+.2f}"
            ]
            x_ay = self.center_x + base_car_scaled.get_width()//2
            for i, line in enumerate(lines_ay):
                surf = self.font.render(line, True, (255, 255, 255))
                rect_text = surf.get_rect(center=(x_ay, y_start + i * self.font.get_linesize()))
                self.screen.blit(surf, rect_text)

            # --- Draw graph under the car ---
            if self.show_graph:
                self._draw_graph(center_x=self.center_x, top_y=self.center_y + base_car_scaled.get_height()//2 + 20)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        print("[INFO] Display closed.")

    # --------------------------
    # Graph overlay with magnitude and time axes
    # --------------------------
    def _draw_graph(self, center_x=0, top_y=0):
        if len(self.graph_history) < 2:
            return

        width, height = 600, 200  # graph size
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 150))  # semi-transparent background

        pts = np.array(self.graph_history)

        # --- Draw signals ---
        for color, idx in [((255, 0, 0), 0), ((0, 255, 0), 1)]:
            scaled = height//2 - pts[:, idx]*50  # scale magnitude
            xvals = np.linspace(0, width, len(scaled))
            for i in range(1, len(xvals)):
                pygame.draw.line(
                    surf, color,
                    (xvals[i-1], scaled[i-1]),
                    (xvals[i], scaled[i]),
                    2
                )

        # --- Draw axes ---
        pygame.draw.line(surf, (200, 200, 200), (0, height//2), (width, height//2), 2)  # horizontal (magnitude=0)
        pygame.draw.line(surf, (200, 200, 200), (0, 0), (0, height), 2)  # vertical (time axis)

        # --- Draw Y-axis labels (magnitude) ---
        font_small = pygame.font.SysFont("consolas", 16)
        for mag in [-2.0, -1.0, 0, 1.0, 2.0]:  # example range
            y = height//2 - mag*50
            pygame.draw.line(surf, (200,200,200), (0, y), (5, y), 2)
            label = font_small.render(f"{mag:+.1f}", True, (255,255,255))
            surf.blit(label, (10, y - 8))

        # --- Blit graph centered horizontally at center_x ---
        self.screen.blit(surf, (center_x - width//2, top_y))


