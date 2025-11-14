import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 2 – Fear & Aggression")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)


# ------------------------------------------------------------
# GLOWING STATIC LIGHT SOURCES
# ------------------------------------------------------------

class Light:
    def __init__(self, x, y, radius=10):
        self.x = x
        self.y = y
        self.radius = radius

    def pos(self):
        return (self.x, self.y)

    def draw(self, surface):
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for i in range(12, 0, -1):
            alpha = int(15 * i)
            size = self.radius * i
            pygame.draw.circle(glow, (255, 255, 120, alpha), (self.x, self.y), size)

        surface.blit(glow, (0, 0))

        pygame.draw.circle(surface, (255, 255, 100), (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (self.x, self.y), self.radius, 2)


# ------------------------------------------------------------
# VEHICLE 2 (Fear & Aggression)
# ------------------------------------------------------------

class Vehicle2:
    def __init__(self, x, y, mode="aggression", radius=22, heading=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading

        self.mode = mode
        self.inverse_mode = False

        self.sensor_dist = radius + 10
        self.sensor_offset = math.radians(30)

        self.left_speed = 0
        self.right_speed = 0
        self.max_speed = 4.5

        self.color = (80, 150, 255) if mode == "fear" else (255, 100, 80)

    def toggle_inverse(self):
        self.inverse_mode = not self.inverse_mode

    def _sensor_positions(self):
        lx = self.x + math.cos(self.heading + self.sensor_offset) * self.sensor_dist
        ly = self.y + math.sin(self.heading + self.sensor_offset) * self.sensor_dist

        rx = self.x + math.cos(self.heading - self.sensor_offset) * self.sensor_dist
        ry = self.y + math.sin(self.heading - self.sensor_offset) * self.sensor_dist

        return (lx, ly), (rx, ry)

    def _intensity(self, sx, sy, lights):
        total = 0
        for L in lights:
            dx = L.x - sx
            dy = L.y - sy
            dist = math.sqrt(dx * dx + dy * dy)
            total += min(1.0 / (0.1 + dist * 0.05), 1.0)

        return min(total, 1.0)

    def update(self, lights):
        (lsx, lsy), (rsx, rsy) = self._sensor_positions()

        left_intensity = self._intensity(lsx, lsy, lights)
        right_intensity = self._intensity(rsx, rsy, lights)

        if self.mode == "aggression":
            if not self.inverse_mode:
                self.left_speed = right_intensity * self.max_speed
                self.right_speed = left_intensity * self.max_speed
            else:
                self.left_speed = (1 - right_intensity) * self.max_speed
                self.right_speed = (1 - left_intensity) * self.max_speed

        elif self.mode == "fear":
            if not self.inverse_mode:
                self.left_speed = left_intensity * self.max_speed
                self.right_speed = right_intensity * self.max_speed
            else:
                self.left_speed = (1 - left_intensity) * self.max_speed
                self.right_speed = (1 - right_intensity) * self.max_speed

        rotation = (self.right_speed - self.left_speed) * 0.04
        self.heading += rotation

        forward = (self.left_speed + self.right_speed) / 2
        self.x += forward * math.cos(self.heading)
        self.y += forward * math.sin(self.heading)

        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)

        (lsx, lsy), (rsx, rsy) = self._sensor_positions()
        pygame.draw.circle(surface, (255, 50, 50), (int(lsx), int(lsy)), 6)
        pygame.draw.circle(surface, (255, 50, 50), (int(rsx), int(rsy)), 6)

        hx = self.x + math.cos(self.heading) * (self.radius + 12)
        hy = self.y + math.sin(self.heading) * (self.radius + 12)
        pygame.draw.line(surface, (0, 0, 0), (self.x, self.y), (hx, hy), 3)

        # -------------------------------
        # FIXED LABEL (now updates!)
        # -------------------------------
        mode_text = self.mode.upper()
        mode_text += " (INVERSE)" if self.inverse_mode else " (NORMAL)"

        label = font.render(mode_text, True, self.color)
        surface.blit(label, (self.x - 40, self.y - self.radius - 20))


# ------------------------------------------------------------
# SETUP
# ------------------------------------------------------------

lights = [
    Light(200, 150),
    Light(800, 180),
    Light(300, 500),
    Light(750, 550)
]

vehicle_fear = Vehicle2(
    random.randint(100, 900),
    random.randint(100, 600),
    mode="fear",
    heading=random.uniform(0, 2 * math.pi)
)

vehicle_agg = Vehicle2(
    random.randint(100, 900),
    random.randint(100, 600),
    mode="aggression",
    heading=random.uniform(0, 2 * math.pi)
)


# ------------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------------

running = True
while running:
    screen.fill((15, 15, 15))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            vehicle_fear.toggle_inverse()
            vehicle_agg.toggle_inverse()

        # Add light on mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            lights.append(Light(mx, my))

    for L in lights:
        L.draw(screen)

    vehicle_fear.update(lights)
    vehicle_agg.update(lights)

    vehicle_fear.draw(screen)
    vehicle_agg.draw(screen)

    ui = pygame.Surface((320, 110), pygame.SRCALPHA)
    ui.fill((255, 255, 255, 210))
    screen.blit(ui, (10, 10))

    t1 = font.render("Fear Vehicle:", True, (0, 0, 0))
    s1 = font.render(f"L={vehicle_fear.left_speed:.2f}  R={vehicle_fear.right_speed:.2f}", True, (0, 0, 0))

    t2 = font.render("Aggressive Vehicle:", True, (0, 0, 0))
    s2 = font.render(f"L={vehicle_agg.left_speed:.2f}  R={vehicle_agg.right_speed:.2f}", True, (0, 0, 0))

    screen.blit(t1, (20, 20))
    screen.blit(s1, (20, 40))

    screen.blit(t2, (20, 70))
    screen.blit(s2, (20, 90))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
