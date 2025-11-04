import pygame
import math
import random

pygame.init()

# Window setup
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Braitenberg Vehicle 1")

clock = pygame.time.Clock()
fps = 60
font = pygame.font.SysFont("consolas", 18)


class VehicleOne:
    def __init__(self, x, y, radius=20, heading=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius
        self.speed = 0
        self.inverse_mode = False

    def toggle_mode(self):
        self.inverse_mode = not self.inverse_mode

    def _sensor_position(self):
        return (self.x + math.cos(self.heading) * self.sensor_dist,
                self.y + math.sin(self.heading) * self.sensor_dist)

    def _intensity_at(self, px, py, lx, ly):
        dx = lx - px
        dy = ly - py
        dist = math.sqrt(dx * dx + dy * dy)
        return min(1.0 / (0.1 + dist * 0.05), 1.0)

    def update(self, light_pos):
        sensor = self._sensor_position()
        intensity = self._intensity_at(sensor[0], sensor[1], light_pos[0], light_pos[1])
        self.speed = (1 - intensity if self.inverse_mode else intensity) * 5.0

        self.x += self.speed * math.cos(self.heading)
        self.y += self.speed * math.sin(self.heading)
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        # Vehicle body
        pygame.draw.circle(surface, (50, 100, 255), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (220, 220, 220), (int(self.x), int(self.y)), self.radius, 2)

        # Sensor
        sensor = self._sensor_position()
        pygame.draw.circle(surface, (255, 50, 50), (int(sensor[0]), int(sensor[1])), 6)

        # Heading line
        end_x = self.x + math.cos(self.heading) * (self.radius + 12)
        end_y = self.y + math.sin(self.heading) * (self.radius + 12)
        pygame.draw.line(surface, (0, 0, 0), (self.x, self.y), (end_x, end_y), 3)


class Light:
    def __init__(self, x, y, radius=9):
        self.x, self.y = x, y
        self.radius = radius

    def move_light(self, pos):
        self.x, self.y = pos

    def pos(self):
        return (self.x, self.y)

    def draw(self, surface):
        # Glow
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(8, 0, -1):
            alpha = int(25 * i)
            size = self.radius * i * 2
            pygame.draw.circle(glow_surface, (255, 255, 120, alpha), (int(self.x), int(self.y)), size)
        surface.blit(glow_surface, (0, 0))

        # Center bright light
        pygame.draw.circle(surface, (255, 255, 50), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)


# Initialize
light = Light(WIDTH // 2, HEIGHT // 2)

vehicle1 = VehicleOne(random.randint(50, WIDTH-50),
                     random.randint(50, HEIGHT-50),
                     radius=20,
                     heading=random.uniform(0, 2 * math.pi))

# vehicle2-code
# vehicle2 = VehicleOne(random.randint(50, WIDTH-50),
#                      random.randint(50, HEIGHT-50),
#                      radius=20,
#                      heading=random.uniform(0, 2 * math.pi))

running = True
while running:
    screen.fill((0,0,0))  # light gray background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            light.move_light(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                vehicle1.toggle_mode()
                # vehicle2.toggle_mode() # vehicle2

    # Generate random stars
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(15)]

    # Draw stars
    for sx, sy, sr in stars:
        brightness = random.randint(150, 255)
        pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), sr)

    # Draw and update
    light.draw(screen)
    vehicle1.update(light.pos())
    vehicle1.draw(screen)

    # vehicle2.update(light.pos()) # vehicle 2
    # vehicle2.draw(screen)


    # UI overlay
    overlay_rect = pygame.Surface((250, 50), pygame.SRCALPHA)
    overlay_rect.fill((255, 255, 255, 200))  # semi-transparent background
    screen.blit(overlay_rect, (10, 10))

    speed_text = font.render(f"Speed: {vehicle1.speed:.2f}", True, (0, 0, 0))
    mode_text = font.render(
        f"Mode: {'Inverse (avoids)' if vehicle1.inverse_mode else 'Normal (seeks)'}",
        True, (0, 0, 0))
    screen.blit(speed_text, (20, 15))
    screen.blit(mode_text, (20, 35))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
