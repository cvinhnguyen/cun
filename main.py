from __future__ import annotations
import random
from math import sin, cos, pi, log, sqrt
import math  # Add this line instead
import time
from tkinter import *

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480
CANVAS_CENTERE_X = CANVAS_WIDTH // 2
CANVAS_CENTERE_Y = CANVAS_HEIGHT // 2
IMAGE_ENLARGE = 11
HEART_COLOR = "#ff3366"  # A softer, more vibrant pink
EDGE_COLOR = "#ff99aa"  # Light pink for edges
CANVAS_COLOR = "#000000"  # Dark blue background
GLOW_COLOR = "#ff6b8b"  # Soft glow color

def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))  # Add negative sign here

    x *= shrink_ratio
    y *= shrink_ratio

    x += CANVAS_CENTERE_X
    y += CANVAS_CENTERE_Y

    return int(x), int(y)

def scatter_inside(x, y , beta=0.15):
    ratio_x = - beta * log(random.random())
    ratio_y = - beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTERE_X)
    dy = ratio_y * (y - CANVAS_CENTERE_Y)

    return x - dx, y - dy

def shrink(x, y, ratio):
    force = -1 / (((x - CANVAS_CENTERE_X) ** 2 + (y - CANVAS_CENTERE_Y) ** 2) ** 0.6 )

    dx = force * (x - CANVAS_CENTERE_X) * ratio
    dy = force * (y - CANVAS_CENTERE_Y) * ratio

    return x - dx, y - dy

def curve(p):
    return 2 * (2 * sin(4*p)) / (2 * pi)

class Heart:

    def __init__(self, generate_frame=60):
        self._points = set()
        self._edge_diffusion_points = set()
        self._center_diffusion_points = set()
        self.all_points = {}
        self.build(4000)  # Increase number of points for more detail
        self.random_halo = 1000
        self.rotation_angle = 0  # Add this line
        self.flip_progress = 0  # Thêm biến này để theo dõi tiến trình lật
        self.flipping = False  # Bin để kiểm soát khi nào bắt đầu lật

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, n):
        for _ in range(n):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))

        for _x,_y in self._points:
            for _ in range(3):
                x, y = scatter_inside(_x, _y, 0.05)
                self._edge_diffusion_points.add((x, y))

        point_list = list(self._points)
        for _ in range(4000):
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.17)
            self._center_diffusion_points.add((x, y))
        
        # Add one mini heart
        self.add_mini_heart()
        self.add_glow_effect()  # New method for adding glow
        self.add_sparkles()  # New method for adding sparkles

    def add_mini_heart(self):
        # Center of the mini heart (aligned with the center of the main heart)
        cx = CANVAS_CENTERE_X
        cy = CANVAS_CENTERE_Y

        # Size of the mini heart (about 30% of the main heart)
        size = 0.3

        # Generate points for the mini heart
        for _ in range(200):  # Adjust the number of points as needed
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio=IMAGE_ENLARGE * size)
            x += cx - CANVAS_CENTERE_X
            y += cy - CANVAS_CENTERE_Y
            self._center_diffusion_points.add((int(x), int(y)))

    def add_glow_effect(self):
        for x, y in self._points:
            for _ in range(4):  # Increase glow points
                angle = random.uniform(0, 2 * pi)
                distance = random.uniform(1, 7)  # Increase glow range
                glow_x = x + cos(angle) * distance
                glow_y = y + sin(angle) * distance
                self._edge_diffusion_points.add((int(glow_x), int(glow_y)))

    def add_sparkles(self):
        self.sparkles = []
        for _ in range(50):  # Add 50 sparkles
            x = random.randint(0, CANVAS_WIDTH)
            y = random.randint(0, CANVAS_HEIGHT)
            size = random.uniform(0.5, 2)
            self.sparkles.append((x, y, size))

    def calc_position(self, x, y, ratio):
        # Calculate the position relative to the center
        rx = x - CANVAS_CENTERE_X
        ry = y - CANVAS_CENTERE_Y

        if self.flipping:
            # Apply 3D rotation effect
            flip_progress = math.sin(math.pi * self.flip_progress)
            rx = rx * math.cos(math.pi * flip_progress)

        # Apply the rotated position
        x = rx + CANVAS_CENTERE_X
        y = ry + CANVAS_CENTERE_Y

        # Apply the shrinking effect
        force = -1 / (((x - CANVAS_CENTERE_X) ** 2 + (y - CANVAS_CENTERE_Y) ** 2) ** 0.520)
        dx = ratio * force * (x - CANVAS_CENTERE_X) + random.randint(-1, 1)
        dy = ratio * force * (y - CANVAS_CENTERE_Y) + random.randint(-1, 1)

        return x - dx, y + dy
    
    def calc(self, generate_frame):
        # Start flipping every 120 frames
        if generate_frame % 120 == 0:
            self.flipping = True
            self.flip_progress = 0

        if self.flipping:
            self.flip_progress += 0.02  # Adjust flipping speed
            if self.flip_progress >= 1:
                self.flipping = False
                self.flip_progress = 0

        ratio = 10 * curve(generate_frame / 10 * pi)

        halo_radius = int(4 + 6 * (1 + curve(generate_frame / 10 * pi)))
        halo_number = int(3000 + 4000 * abs(curve(generate_frame / 10 * pi) ** 2))

        all_points = []

        heart_halo_points = set()
        for _ in range(halo_number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t, shrink_ratio = 11.6)
            x, y = shrink(x, y, halo_radius)
            if (x, y) not in heart_halo_points:
                heart_halo_points.add((x, y))
                x += random.randint(-14, 14)
                y += random.randint(-14, 14)
                size = random.choice((1,2,2))
                all_points.append((x, y, size))

        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 3)
            all_points.append((x, y, size))

        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size))

        self.all_points[generate_frame] = all_points  # Store points for this frame

    def render(self, render_canvas, render_frame):
        render_canvas.delete("all")
        render_canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill=CANVAS_COLOR, outline=CANVAS_COLOR)

        # Draw glow effect
        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, 10 * curve(render_frame / 10 * pi))  # Apply rotation to glow
            size = random.uniform(1.5, 3.5)
            render_canvas.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, fill=GLOW_COLOR, outline="")

        # Draw main heart points
        for x, y, size in self.all_points[render_frame % self.generate_frame]:
            render_canvas.create_oval(x, y, x + size, y + size, fill=HEART_COLOR, outline="")

        # Draw sparkles
        for x, y, size in self.sparkles:
            if random.random() < 0.2:  # Only show some sparkles each frame
                render_canvas.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, fill="white", outline="")

# Move the draw function outside of the Heart class
def draw(main: Tk, render_canvas: Canvas, render_heart: Heart, render_frame=0):
    render_heart.render(render_canvas, render_frame)
    main.after(16, draw, main, render_canvas, render_heart, render_frame + 1)  # ~60 FPS

if __name__ == "__main__":
    root = Tk()
    canvas = Canvas(root, width = CANVAS_WIDTH, height = CANVAS_HEIGHT, bg = "black")
    canvas.pack()
    heart = Heart()
    
    # Start the drawing process
    draw(root, canvas, heart)
    
    # Start the Tkinter event loop
    root.mainloop()
