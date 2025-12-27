import pygame
import random
import math
import sys
from enum import Enum
from dataclasses import dataclass

pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
PURPLE = (180, 50, 255)
CYAN = (0, 255, 255)
DARK_BLUE = (15, 20, 45)
PINK = (255, 100, 180)
LIME = (150, 255, 0)
DARK_RED = (150, 0, 0)
GOLD = (255, 215, 0)

@dataclass
class GameStats:
    high_score: int = 0
    total_kills: int = 0
    bosses_defeated: int = 0
    games_played: int = 0
    powerups_collected: int = 0

class SoundManager:
    """Manages game sounds with procedural generation"""
    def __init__(self):
        self.enabled = True
        self.volume = 0.3
        
    def play_shoot(self):
        if not self.enabled:
            return
        try:
            duration = 100
            frequency = 440
            sample_rate = 22050
            n_samples = int(duration * sample_rate / 1000)
            
            # Generate shooting sound
            buf = []
            for i in range(n_samples):
                t = float(i) / sample_rate
                value = int(32767.0 * math.sin(2.0 * math.pi * frequency * t) * (1 - i / n_samples))
                buf.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            sound = pygame.mixer.Sound(bytes(buf))
            sound.set_volume(self.volume * 0.3)
            sound.play()
        except:
            pass
    
    def play_explosion(self):
        if not self.enabled:
            return
        try:
            duration = 200
            sample_rate = 22050
            n_samples = int(duration * sample_rate / 1000)
            
            # Generate explosion sound (white noise)
            buf = []
            for i in range(n_samples):
                value = int(random.randint(-32767, 32767) * (1 - i / n_samples))
                buf.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            sound = pygame.mixer.Sound(bytes(buf))
            sound.set_volume(self.volume * 0.4)
            sound.play()
        except:
            pass
    
    def play_powerup(self):
        if not self.enabled:
            return
        try:
            duration = 150
            sample_rate = 22050
            n_samples = int(duration * sample_rate / 1000)
            
            # Generate powerup sound (rising tone)
            buf = []
            for i in range(n_samples):
                t = float(i) / sample_rate
                freq = 440 + (i / n_samples) * 440
                value = int(32767.0 * math.sin(2.0 * math.pi * freq * t) * (1 - i / n_samples))
                buf.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            sound = pygame.mixer.Sound(bytes(buf))
            sound.set_volume(self.volume * 0.5)
            sound.play()
        except:
            pass
    
    def play_damage(self):
        if not self.enabled:
            return
        try:
            duration = 120
            sample_rate = 22050
            n_samples = int(duration * sample_rate / 1000)
            
            # Generate damage sound (low frequency pulse)
            buf = []
            for i in range(n_samples):
                t = float(i) / sample_rate
                value = int(32767.0 * math.sin(2.0 * math.pi * 110 * t) * (1 - i / n_samples))
                buf.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            sound = pygame.mixer.Sound(bytes(buf))
            sound.set_volume(self.volume * 0.6)
            sound.play()
        except:
            pass

class PowerUpType(Enum):
    RAPID_FIRE = 1
    SHIELD = 2
    HEALTH = 3

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 3)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
        self.twinkle = random.uniform(0, math.pi * 2)
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
        self.twinkle += 0.05
    
    def draw(self, screen):
        twinkle_factor = (math.sin(self.twinkle) + 1) / 2
        brightness = int(self.brightness * (0.5 + 0.5 * twinkle_factor))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Particle:
    def __init__(self, x, y, color, size=5, velocity=None):
        self.x = x
        self.y = y
        self.color = color
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        self.life = 60
        self.max_life = 60
        self.size = size
        self.gravity = random.uniform(0, 0.3)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size = max(1, self.size * (self.life / self.max_life))
        self.vx *= 0.97
        self.vy *= 0.97
    
    def draw(self, screen):
        if self.life > 0:
            alpha_factor = self.life / self.max_life
            color = tuple(int(c * alpha_factor) for c in self.color[:3])
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=12, color=YELLOW, damage=15, is_enemy=False, homing=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_enemy = is_enemy
        self.color = color
        self.homing = homing
        self.speed = speed
        angle = math.atan2(target_y - y, target_x - x)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = 5 if is_enemy else 4
        self.trail = []
    
    def update(self, target_x=None, target_y=None):
        if self.homing and target_x and target_y:
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.vx += math.cos(angle) * 0.4
            self.vy += math.sin(angle) * 0.4
            speed = math.hypot(self.vx, self.vy)
            if speed > self.speed:
                self.vx = (self.vx / speed) * self.speed
                self.vy = (self.vy / speed) * self.speed
        
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        
        self.x += self.vx
        self.y += self.vy
    
    def draw(self, screen):
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            size = int(self.radius * (i + 1) / len(self.trail))
            alpha_factor = (i + 1) / len(self.trail)
            color = tuple(int(c * alpha_factor * 0.7) for c in self.color[:3])
            pygame.draw.circle(screen, color, (int(tx), int(ty)), size)
        
        # Draw main bullet
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 1)
        
        # Draw glow for enemy bullets
        if self.is_enemy:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius + 2, 1)
    
    def is_off_screen(self):
        margin = 100
        return (self.x < -margin or self.x > WIDTH + margin or 
                self.y < -margin or self.y > HEIGHT + margin)

class PowerUp:
    def __init__(self, x, y, power_type=None):
        self.x = x
        self.y = y
        self.type = power_type if power_type else random.choice(list(PowerUpType))
        self.radius = 20
        self.collected = False
        self.rotation = 0
        self.pulse = 0
        
        self.colors = {
            PowerUpType.RAPID_FIRE: (ORANGE, RED),
            PowerUpType.SHIELD: (CYAN, BLUE),
            PowerUpType.HEALTH: (GREEN, LIME)
        }
        
        self.icons = {
            PowerUpType.RAPID_FIRE: "R",
            PowerUpType.SHIELD: "S",
            PowerUpType.HEALTH: "+"
        }
    
    def update(self):
        self.y += 2
        self.rotation += 4
        self.pulse += 0.1
    
    def draw(self, screen):
        color1, color2 = self.colors[self.type]
        
        # Pulsing effect
        pulse_size = abs(math.sin(self.pulse)) * 6
        radius = self.radius + pulse_size
        
        # Outer glow rings
        for i in range(4):
            glow_radius = radius + (4 - i) * 4
            alpha = 30 + i * 20
            glow_color = tuple(min(255, c + alpha) for c in color2[:3])
            pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), int(glow_radius), 2)
        
        # Main circle with gradient effect
        pygame.draw.circle(screen, color1, (int(self.x), int(self.y)), int(radius))
        pygame.draw.circle(screen, color2, (int(self.x), int(self.y)), int(radius - 4))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(radius), 3)
        
        # Rotating icon
        font = pygame.font.Font(None, 32)
        text = self.icons[self.type]
        text_surf = font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text_surf, text_rect)
        
        # Small particles around powerup
        for i in range(4):
            angle = self.rotation * 0.05 + (i * math.pi / 2)
            px = self.x + math.cos(angle) * (radius + 8)
            py = self.y + math.sin(angle) * (radius + 8)
            pygame.draw.circle(screen, WHITE, (int(px), int(py)), 2)

class Player:
    def __init__(self, x, y, sound_manager):
        self.x = x
        self.y = y
        self.health = 100
        self.max_health = 100
        self.base_speed = 6
        self.speed = self.base_speed
        self.radius = 20
        self.color = BLUE
        self.shoot_cooldown = 0
        self.base_shoot_delay = 12
        self.shoot_delay = self.base_shoot_delay
        self.sound_manager = sound_manager
        
        # Powerup timers
        self.rapid_fire_time = 0
        self.shield_time = 0
        
        # Visual effects
        self.engine_particles = []
        self.angle = 0
        self.invulnerable_frames = 0
        self.hit_flash = 0
    
    def update(self, keys):
        # Movement
        dx, dy = 0, 0
        if keys[pygame.K_w] and self.y > self.radius + 10:
            dy = -self.speed
        if keys[pygame.K_s] and self.y < HEIGHT - self.radius - 10:
            dy = self.speed
        if keys[pygame.K_a] and self.x > self.radius + 10:
            dx = -self.speed
        if keys[pygame.K_d] and self.x < WIDTH - self.radius - 10:
            dx = self.speed
        
        # Diagonal movement normalization
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        self.x += dx
        self.y += dy
        
        # Update angle for aiming
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        
        # Cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if self.invulnerable_frames > 0:
            self.invulnerable_frames -= 1
        
        if self.hit_flash > 0:
            self.hit_flash -= 1
        
        # Powerup effects
        if self.rapid_fire_time > 0:
            self.rapid_fire_time -= 1
            self.shoot_delay = 4
        else:
            self.shoot_delay = self.base_shoot_delay
        
        if self.shield_time > 0:
            self.shield_time -= 1
        
        # Engine particles
        if dx != 0 or dy != 0:
            offset_x = -math.cos(self.angle) * self.radius * 0.8
            offset_y = -math.sin(self.angle) * self.radius * 0.8
            
            # Add engine particles
            if random.random() < 0.5:
                self.engine_particles.append(Particle(
                    self.x + offset_x + random.uniform(-3, 3), 
                    self.y + offset_y + random.uniform(-3, 3), 
                    CYAN if self.rapid_fire_time > 0 else ORANGE,
                    random.randint(2, 4),
                    (-self.vx if hasattr(self, 'vx') else 0, -self.vy if hasattr(self, 'vy') else 0)
                ))
        
        self.vx = dx
        self.vy = dy
        
        # Update engine particles
        for particle in self.engine_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.engine_particles.remove(particle)
    
    def shoot(self, mouse_x, mouse_y):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = self.shoot_delay
            self.sound_manager.play_shoot()
            return [Bullet(self.x, self.y, mouse_x, mouse_y, damage=25, color=YELLOW)]
        return []
    
    def take_damage(self, damage):
        if self.shield_time <= 0 and self.invulnerable_frames <= 0:
            self.health -= damage
            self.invulnerable_frames = 40
            self.hit_flash = 20
            self.sound_manager.play_damage()
            return True
        return False
    
    def apply_powerup(self, powerup_type):
        self.sound_manager.play_powerup()
        if powerup_type == PowerUpType.RAPID_FIRE:
            self.rapid_fire_time = 420
        elif powerup_type == PowerUpType.SHIELD:
            self.shield_time = 480
        elif powerup_type == PowerUpType.HEALTH:
            self.health = min(self.max_health, self.health + 40)
    
    def draw(self, screen):
        # Draw engine particles
        for particle in self.engine_particles:
            particle.draw(screen)
        
        # Draw shield
        if self.shield_time > 0:
            shield_radius = self.radius + 10
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 4
            
            # Shield layers
            for i in range(3):
                radius = shield_radius + pulse - i * 3
                alpha = 150 - i * 40
                color = tuple(c * alpha // 255 for c in CYAN[:3])
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(radius), 2)
        
        # Invulnerability flash
        if self.invulnerable_frames > 0 and self.invulnerable_frames % 8 < 4:
            return
        
        # Draw player ship (advanced triangle design)
        points = []
        
        # Main triangle
        for angle_offset in [0, 2.5, -2.5]:
            px = self.x + math.cos(self.angle + angle_offset) * self.radius
            py = self.y + math.sin(self.angle + angle_offset) * self.radius
            points.append((px, py))
        
        # Fill with gradient effect
        if self.hit_flash > 0:
            ship_color = RED
        elif self.rapid_fire_time > 0:
            ship_color = ORANGE
        else:
            ship_color = self.color
        
        pygame.draw.polygon(screen, ship_color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Wings
        wing_points_left = [
            (self.x, self.y),
            (self.x + math.cos(self.angle + 2.2) * self.radius * 0.7,
             self.y + math.sin(self.angle + 2.2) * self.radius * 0.7),
            (self.x + math.cos(self.angle + 1.8) * self.radius * 1.2,
             self.y + math.sin(self.angle + 1.8) * self.radius * 1.2)
        ]
        
        wing_points_right = [
            (self.x, self.y),
            (self.x + math.cos(self.angle - 2.2) * self.radius * 0.7,
             self.y + math.sin(self.angle - 2.2) * self.radius * 0.7),
            (self.x + math.cos(self.angle - 1.8) * self.radius * 1.2,
             self.y + math.sin(self.angle - 1.8) * self.radius * 1.2)
        ]
        
        pygame.draw.polygon(screen, DARK_BLUE, wing_points_left)
        pygame.draw.polygon(screen, DARK_BLUE, wing_points_right)
        pygame.draw.polygon(screen, CYAN, wing_points_left, 1)
        pygame.draw.polygon(screen, CYAN, wing_points_right, 1)
        
        # Cockpit
        cockpit_x = self.x + math.cos(self.angle) * (self.radius * 0.3)
        cockpit_y = self.y + math.sin(self.angle) * (self.radius * 0.3)
        pygame.draw.circle(screen, CYAN, (int(cockpit_x), int(cockpit_y)), 5)
        pygame.draw.circle(screen, WHITE, (int(cockpit_x), int(cockpit_y)), 5, 1)
        
        # Draw health bar
        self.draw_health_bar(screen)
    
    def draw_health_bar(self, screen):
        bar_width = 70
        bar_height = 10
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 20
        
        # Background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int(bar_width * (self.health / self.max_health))
        if self.health > 70:
            health_color = GREEN
        elif self.health > 35:
            health_color = YELLOW
        else:
            health_color = RED
        
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        font = pygame.font.Font(None, 16)
        health_text = font.render(f"{self.health}", True, WHITE)
        text_rect = health_text.get_rect(center=(self.x, bar_y + bar_height // 2))
        screen.blit(health_text, text_rect)

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.x = x
        self.y = y
        self.type = enemy_type
        
        # Type-specific stats
        if enemy_type == "normal":
            self.health = 50
            self.speed = 2.8
            self.radius = 16
            self.color = RED
            self.damage = 15
            self.score_value = 10
        elif enemy_type == "shooter":
            self.health = 70
            self.speed = 2.0
            self.radius = 18
            self.color = PURPLE
            self.damage = 12
            self.score_value = 25
        
        self.max_health = self.health
        self.shoot_cooldown = 0
        self.angle = 0
        self.rotation = 0
    
    def update(self, player_x, player_y):
        # Move toward player
        self.angle = math.atan2(player_y - self.y, player_x - self.x)
        
        if self.type == "shooter":
            # Shooters keep distance
            dist = math.hypot(player_x - self.x, player_y - self.y)
            if dist < 250:
                self.x -= math.cos(self.angle) * self.speed * 0.7
                self.y -= math.sin(self.angle) * self.speed * 0.7
            elif dist > 350:
                self.x += math.cos(self.angle) * self.speed
                self.y += math.sin(self.angle) * self.speed
        else:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
        
        self.rotation += 3
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def shoot(self, player_x, player_y):
        if self.type == "shooter" and self.shoot_cooldown == 0:
            self.shoot_cooldown = 90
            return Bullet(self.x, self.y, player_x, player_y, speed=6, 
                         color=self.color, damage=18, is_enemy=True)
        return None
    
    def draw(self, screen):
        # Draw enemy with rotation
        if self.type == "shooter":
            # Hexagon for shooter
            points = []
            for i in range(6):
                angle = (math.pi / 3) * i + (self.rotation * 0.02)
                px = self.x + math.cos(angle) * self.radius
                py = self.y + math.sin(angle) * self.radius
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            
            # Inner circle
            pygame.draw.circle(screen, DARK_RED, (int(self.x), int(self.y)), self.radius // 2)
        else:
            # Triangle for normal
            points = []
            for i in range(3):
                angle = self.angle + (i * 2 * math.pi / 3) + (self.rotation * 0.01)
                px = self.x + math.cos(angle) * self.radius
                py = self.y + math.sin(angle) * self.radius
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Core glow
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), 4)
        
        # Health bar
        bar_width = self.radius * 2.5
        bar_height = 5
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 12
        
        pygame.draw.rect(screen, (40, 40, 40), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = GREEN if self.health > self.max_health * 0.5 else YELLOW
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

class Boss:
    def __init__(self, wave, sound_manager):
        self.x = WIDTH // 2
        self.y = -120
        self.target_y = 130
        self.wave = wave
        self.health = 500 + (wave * 150)
        self.max_health = self.health
        self.radius = 55
        self.color = ORANGE
        self.speed = 5
        self.direction = 1
        self.shoot_cooldown = 0
        self.special_cooldown = 0
        self.phase = 1
        self.entering = True
        self.rotation = 0
        self.sound_manager = sound_manager
        
    def update(self):
        # Entry animation
        if self.entering:
            if self.y < self.target_y:
                self.y += 4
            else:
                self.entering = False
        
        # Movement pattern
        if not self.entering:
            self.x += self.speed * self.direction
            if self.x <= self.radius + 60 or self.x >= WIDTH - self.radius - 60:
                self.direction *= -1
        
        self.rotation += 3
        
        # Phase changes based on health
        health_percent = self.health / self.max_health
        if health_percent < 0.25:
            self.phase = 3
            self.speed = 7
        elif health_percent < 0.6:
            self.phase = 2
            self.speed = 6
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
    
    def shoot(self, player_x, player_y):
        bullets = []
        
        if self.entering:
            return bullets
        
        # Normal attack
        if self.shoot_cooldown == 0:
            if self.phase == 1:
                self.shoot_cooldown = 45
                # Triple shot
                for angle_offset in [-0.3, 0, 0.3]:
                    angle = math.atan2(player_y - self.y, player_x - self.x) + angle_offset
                    target_x = self.x + math.cos(angle) * 300
                    target_y = self.y + math.sin(angle) * 300
                    bullets.append(Bullet(self.x, self.y, target_x, target_y, 
                                        speed=7, color=ORANGE, damage=22, is_enemy=True))
            
            elif self.phase == 2:
                self.shoot_cooldown = 35
                # Five shot spread
                for angle_offset in [-0.5, -0.25, 0, 0.25, 0.5]:
                    angle = math.atan2(player_y - self.y, player_x - self.x) + angle_offset
                    target_x = self.x + math.cos(angle) * 300
                    target_y = self.y + math.sin(angle) * 300
                    bullets.append(Bullet(self.x, self.y, target_x, target_y,
                                        speed=8, color=RED, damage=28, is_enemy=True))
            
            else:  # phase 3
                self.shoot_cooldown = 25
                # Homing missiles
                for _ in range(3):
                    bullets.append(Bullet(self.x + random.randint(-20, 20), 
                                        self.y + random.randint(-20, 20), 
                                        player_x, player_y,
                                        speed=5, color=PINK, damage=35, is_enemy=True, homing=True))
        
        # Special attacks
        if self.special_cooldown == 0:
            if self.phase == 1:
                self.special_cooldown = 200
                # Circular burst
                for i in range(16):
                    angle = (math.pi * 2 / 16) * i
                    target_x = self.x + math.cos(angle) * 300
                    target_y = self.y + math.sin(angle) * 300
                    bullets.append(Bullet(self.x, self.y, target_x, target_y,
                                        speed=5, color=YELLOW, damage=20, is_enemy=True))
            
            elif self.phase == 2:
                self.special_cooldown = 160
                # Spiral pattern
                for i in range(20):
                    angle = (math.pi * 2 / 20) * i + (self.rotation * 0.05)
                    target_x = self.x + math.cos(angle) * 300
                    target_y = self.y + math.sin(angle) * 300
                    bullets.append(Bullet(self.x, self.y, target_x, target_y,
                                        speed=6, color=CYAN, damage=25, is_enemy=True))
            
            else:  # phase 3
                self.special_cooldown = 130
                # Laser walls
                for i in range(7):
                    y_offset = (i - 3) * 60
                    bullets.append(Bullet(self.x - 30, self.y, self.x - 600, self.y + y_offset,
                                        speed=10, color=RED, damage=40, is_enemy=True))
                    bullets.append(Bullet(self.x + 30, self.y, self.x + 600, self.y + y_offset,
                                        speed=10, color=RED, damage=40, is_enemy=True))
        
        return bullets
    
    def draw(self, screen):
        # Outer rotating ring
        for i in range(8):
            angle = (math.pi * 2 / 8) * i + (self.rotation * 0.03)
            px = self.x + math.cos(angle) * (self.radius + 15)
            py = self.y + math.sin(angle) * (self.radius + 15)
            pygame.draw.circle(screen, YELLOW, (int(px), int(py)), 6)
            pygame.draw.circle(screen, ORANGE, (int(px), int(py)), 4)
        
        # Main body layers
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 12)
        pygame.draw.circle(screen, DARK_RED, (int(self.x), int(self.y)), self.radius - 24)
        
        # Armor plates
        for i in range(6):
            angle = (math.pi * 2 / 6) * i - (self.rotation * 0.02)
            px1 = self.x + math.cos(angle) * (self.radius - 8)
            py1 = self.y + math.sin(angle) * (self.radius - 8)
            px2 = self.x + math.cos(angle) * self.radius
            py2 = self.y + math.sin(angle) * self.radius
            pygame.draw.line(screen, GOLD, (int(px1), int(py1)), (int(px2), int(py2)), 3)
        
        # Pulsing core
        pulse = abs(math.sin(self.rotation * 0.1)) * 5
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), int(18 + pulse))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(12 + pulse))
        
        # Outer border
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 3)
        
        # Phase indicator lines
        phase_colors = [ORANGE, RED, PINK]
        for i in range(self.phase):
            offset = (i - 1) * 8
            start_x = self.x - 15
            start_y = self.y + self.radius + 10 + offset
            end_x = self.x + 15
            end_y = start_y
            pygame.draw.line(screen, phase_colors[i], (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), 3)
        
        # Boss health bar (top of screen)
        self.draw_boss_health_bar(screen)
    
    def draw_boss_health_bar(self, screen):
        bar_width = WIDTH - 220
        bar_height = 30
        bar_x = 110
        bar_y = 15
        
        # Shadow
        pygame.draw.rect(screen, (20, 20, 20), (bar_x + 3, bar_y + 3, bar_width, bar_height))
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, DARK_RED, (bar_x + 2, bar_y + 2, bar_width - 4, bar_height - 4))
        
        # Health
        health_width = int((bar_width - 4) * (self.health / self.max_health))
        phase_colors = [ORANGE, RED, PINK]
        health_color = phase_colors[self.phase - 1]
        
        # Gradient effect
        for i in range(health_width):
            alpha = 0.7 + 0.3 * (i / health_width if health_width > 0 else 0)
            color = tuple(int(c * alpha) for c in health_color[:3])
            pygame.draw.line(screen, color, 
                           (bar_x + 2 + i, bar_y + 2), 
                           (bar_x + 2 + i, bar_y + bar_height - 2))
        
        # Segments
        segment_count = 20
        for i in range(1, segment_count):
            seg_x = bar_x + (bar_width * i // segment_count)
            pygame.draw.line(screen, (30, 30, 30), (seg_x, bar_y + 2), (seg_x, bar_y + bar_height - 2), 2)
        
        # Border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)
        pygame.draw.rect(screen, GOLD, (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2), 1)
        
        # Text
        font_large = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 20)
        
        boss_text = font_large.render(f"BOSS - PHASE {self.phase}", True, GOLD)
        health_text = font_small.render(f"{self.health} / {self.max_health}", True, WHITE)
        
        boss_rect = boss_text.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
        health_rect = health_text.get_rect(center=(WIDTH // 2, bar_y + bar_height + 12))
        
        # Text shadow
        shadow_offset = 2
        boss_shadow = font_large.render(f"BOSS - PHASE {self.phase}", True, BLACK)
        screen.blit(boss_shadow, (boss_rect.x + shadow_offset, boss_rect.y + shadow_offset))
        
        screen.blit(boss_text, boss_rect)
        screen.blit(health_text, health_rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Shooter - Complete Edition")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 56)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 28)
        self.font_mini = pygame.font.Font(None, 20)
        
        self.sound_manager = SoundManager()
        self.stats = GameStats()
        self.stars = [Star() for _ in range(150)]
        self.show_menu = True
        self.reset_game()
    
    def reset_game(self):
        self.player = Player(WIDTH // 2, HEIGHT - 100, self.sound_manager)
        self.bullets = []
        self.enemies = []
        self.boss = None
        self.powerups = []
        self.particles = []
        self.score = 0
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.difficulty_timer = 0
        self.wave = 1
        self.kills = 0
        self.kills_for_boss = 20
        self.game_over = False
        self.victory = False
        self.auto_fire = True
        self.paused = False
        self.difficulty_multiplier = 1.0
        self.combo = 0
        self.combo_timer = 0
        self.stats.games_played += 1
    
    def spawn_enemy(self):
        spawn_side = random.choice(['top', 'left', 'right', 'top'])
        
        if spawn_side == 'top':
            x = random.randint(50, WIDTH - 50)
            y = random.randint(-100, -50)
        elif spawn_side == 'left':
            x = random.randint(-100, -50)
            y = random.randint(50, HEIGHT // 2)
        else:
            x = random.randint(WIDTH + 50, WIDTH + 100)
            y = random.randint(50, HEIGHT // 2)
        
        weights = [6, 3] if self.wave < 3 else [5, 4]
        enemy_type = random.choices(['normal', 'shooter'], weights=weights)[0]
        
        self.enemies.append(Enemy(x, y, enemy_type))
    
    def spawn_boss(self):
        self.boss = Boss(self.wave, self.sound_manager)
    
    def spawn_powerup(self, x, y):
        self.powerups.append(PowerUp(x, y))
    
    def create_explosion(self, x, y, color, count=30, size=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, size))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.show_menu and event.key == pygame.K_SPACE:
                    self.show_menu = False
                    self.reset_game()
                elif event.key == pygame.K_SPACE and self.game_over:
                    self.game_over = False
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    if self.game_over:
                        self.show_menu = True
                    elif self.show_menu:
                        return False
                    else:
                        self.paused = not self.paused
                elif event.key == pygame.K_f and not self.game_over and not self.show_menu:
                    self.auto_fire = not self.auto_fire
                elif event.key == pygame.K_m:
                    self.sound_manager.enabled = not self.sound_manager.enabled
            
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.auto_fire and not self.paused and not self.show_menu:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullets = self.player.shoot(mouse_x, mouse_y)
                self.bullets.extend(bullets)
        
        return True
    
    def update(self):
        if self.game_over or self.paused or self.show_menu:
            for star in self.stars:
                star.update()
            return
        
        for star in self.stars:
            star.update()
        
        if self.auto_fire:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            bullets = self.player.shoot(mouse_x, mouse_y)
            self.bullets.extend(bullets)
        
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        for bullet in self.bullets[:]:
            if bullet.homing and not bullet.is_enemy and len(self.enemies) > 0:
                closest = min(self.enemies, key=lambda e: math.hypot(e.x - bullet.x, e.y - bullet.y))
                bullet.update(closest.x, closest.y)
            elif bullet.homing and bullet.is_enemy:
                bullet.update(self.player.x, self.player.y)
            else:
                bullet.update()
            
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        self.difficulty_timer += 1
        if self.difficulty_timer > 900:
            self.difficulty_multiplier += 0.15
            self.difficulty_timer = 0
        
        for enemy in self.enemies[:]:
            enemy.update(self.player.x, self.player.y)
            
            bullet = enemy.shoot(self.player.x, self.player.y)
            if bullet:
                self.bullets.append(bullet)
            
            dist = math.hypot(enemy.x - self.player.x, enemy.y - self.player.y)
            if dist < enemy.radius + self.player.radius:
                if self.player.take_damage(enemy.damage):
                    self.create_explosion(enemy.x, enemy.y, enemy.color, 25, 5)
                self.enemies.remove(enemy)
                continue
            
            if enemy.y > HEIGHT + 150 or enemy.x < -150 or enemy.x > WIDTH + 150:
                self.enemies.remove(enemy)
        
        if self.boss:
            self.boss.update()
            boss_bullets = self.boss.shoot(self.player.x, self.player.y)
            self.bullets.extend(boss_bullets)
            
            dist = math.hypot(self.boss.x - self.player.x, self.boss.y - self.player.y)
            if dist < self.boss.radius + self.player.radius:
                self.player.take_damage(35)
        
        for powerup in self.powerups[:]:
            powerup.update()
            dist = math.hypot(powerup.x - self.player.x, powerup.y - self.player.y)
            if dist < powerup.radius + self.player.radius:
                self.player.apply_powerup(powerup.type)
                self.create_explosion(powerup.x, powerup.y, powerup.colors[powerup.type][0], 20, 4)
                self.stats.powerups_collected += 1
                self.powerups.remove(powerup)
            elif powerup.y > HEIGHT + 100:
                self.powerups.remove(powerup)
        
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        for bullet in self.bullets[:]:
            if bullet.is_enemy:
                dist = math.hypot(bullet.x - self.player.x, bullet.y - self.player.y)
                if dist < self.player.radius + bullet.radius:
                    if self.player.take_damage(bullet.damage):
                        self.create_explosion(bullet.x, bullet.y, YELLOW, 12, 3)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
            else:
                hit = False
                for enemy in self.enemies[:]:
                    dist = math.hypot(bullet.x - enemy.x, bullet.y - enemy.y)
                    if dist < enemy.radius + bullet.radius:
                        enemy.health -= bullet.damage
                        self.create_explosion(bullet.x, bullet.y, YELLOW, 10, 2)
                        
                        if enemy.health <= 0:
                            self.sound_manager.play_explosion()
                            self.create_explosion(enemy.x, enemy.y, enemy.color, 35, 6)
                            
                            self.combo += 1
                            self.combo_timer = 120
                            combo_multiplier = 1 + (self.combo * 0.1)
                            
                            score_gain = int(enemy.score_value * self.difficulty_multiplier * combo_multiplier)
                            self.score += score_gain
                            self.kills += 1
                            self.stats.total_kills += 1
                            
                            drop_chance = 0.3 if self.combo > 5 else 0.2
                            if random.random() < drop_chance:
                                self.spawn_powerup(enemy.x, enemy.y)
                            
                            self.enemies.remove(enemy)
                        
                        hit = True
                        break
                
                if not hit and self.boss:
                    dist = math.hypot(bullet.x - self.boss.x, bullet.y - self.boss.y)
                    if dist < self.boss.radius + bullet.radius:
                        self.boss.health -= bullet.damage
                        self.create_explosion(bullet.x, bullet.y, ORANGE, 12, 3)
                        
                        if self.boss.health <= 0:
                            self.sound_manager.play_explosion()
                            self.create_explosion(self.boss.x, self.boss.y, ORANGE, 100, 10)
                            
                            bonus = int(300 * self.difficulty_multiplier)
                            self.score += bonus
                            self.stats.bosses_defeated += 1
                            
                            for _ in range(4):
                                offset_x = random.randint(-60, 60)
                                offset_y = random.randint(-60, 60)
                                self.spawn_powerup(self.boss.x + offset_x, self.boss.y + offset_y)
                            
                            self.boss = None
                            self.wave += 1
                            self.kills = 0
                        
                        hit = True
                
                if hit and bullet in self.bullets:
                    self.bullets.remove(bullet)
        
        if not self.boss:
            self.enemy_spawn_timer += 1
            spawn_rate = max(15, 45 - int(self.difficulty_multiplier * 8))
            
            if self.enemy_spawn_timer > spawn_rate:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
                
                if random.random() < 0.4 + (self.difficulty_multiplier * 0.1):
                    self.spawn_enemy()
        
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer > 750:
            x = random.randint(120, WIDTH - 120)
            self.spawn_powerup(x, -50)
            self.powerup_spawn_timer = 0
        
        if self.kills >= self.kills_for_boss and not self.boss:
            self.spawn_boss()
            self.kills = 0
            self.kills_for_boss = min(30, int(self.kills_for_boss * 1.3))
        
        if self.player.health <= 0:
            self.game_over = True
            if self.score > self.stats.high_score:
                self.stats.high_score = self.score
    
    def draw_ui(self):
        panel_height = 140
        overlay = pygame.Surface((250, panel_height))
        overlay.set_alpha(180)
        overlay.fill((10, 10, 30))
        self.screen.blit(overlay, (5, 5))
        pygame.draw.rect(self.screen, CYAN, (5, 5, 250, panel_height), 2)
        
        score_text = self.font_small.render(f"Score: {self.score}", True, GOLD)
        self.screen.blit(score_text, (15, 15))
        
        high_text = self.font_tiny.render(f"High: {self.stats.high_score}", True, YELLOW)
        self.screen.blit(high_text, (15, 50))
        
        wave_text = self.font_small.render(f"Wave: {self.wave}", True, CYAN)
        self.screen.blit(wave_text, (15, 80))
        
        if not self.boss:
            kills_text = self.font_tiny.render(f"Boss: {self.kills_for_boss - self.kills} kills", True, ORANGE)
            self.screen.blit(kills_text, (15, 115))
        
        if self.combo > 2:
            combo_text = self.font_medium.render(f"COMBO x{self.combo}!", True, GOLD)
            combo_rect = combo_text.get_rect(center=(WIDTH // 2, 80))
            
            combo_shadow = self.font_medium.render(f"COMBO x{self.combo}!", True, BLACK)
            self.screen.blit(combo_shadow, (combo_rect.x + 3, combo_rect.y + 3))
            self.screen.blit(combo_text, combo_rect)
        
        panel_x = WIDTH - 260
        overlay2 = pygame.Surface((255, 140))
        overlay2.set_alpha(180)
        overlay2.fill((10, 10, 30))
        self.screen.blit(overlay2, (panel_x, 5))
        pygame.draw.rect(self.screen, CYAN, (panel_x, 5, 255, 140), 2)
        
        mode_color = GREEN if self.auto_fire else RED
        mode_text = self.font_tiny.render(f"[F] {'AUTO-FIRE' if self.auto_fire else 'MANUAL'}", True, mode_color)
        self.screen.blit(mode_text, (panel_x + 10, 15))
        
        diff_text = self.font_tiny.render(f"Difficulty: x{self.difficulty_multiplier:.1f}", True, PINK)
        self.screen.blit(diff_text, (panel_x + 10, 45))
        
        sound_text = self.font_mini.render(f"[M] Sound: {'ON' if self.sound_manager.enabled else 'OFF'}", 
                                           True, GREEN if self.sound_manager.enabled else RED)
        self.screen.blit(sound_text, (panel_x + 10, 75))
        
        controls = self.font_mini.render("[ESC] Pause", True, WHITE)
        self.screen.blit(controls, (panel_x + 10, 105))
        
        y_offset = HEIGHT - 50
        if any([self.player.rapid_fire_time > 0, self.player.shield_time > 0]):
            overlay3 = pygame.Surface((280, 80))
            overlay3.set_alpha(180)
            overlay3.fill((10, 10, 30))
            self.screen.blit(overlay3, (10, y_offset - 30))
            pygame.draw.rect(self.screen, CYAN, (10, y_offset - 30, 280, 80), 2)
            
            title = self.font_tiny.render("Active Power-ups:", True, WHITE)
            self.screen.blit(title, (20, y_offset - 20))
        
        powerups_active = []
        if self.player.rapid_fire_time > 0:
            powerups_active.append((f"Rapid Fire: {self.player.rapid_fire_time // 60}s", ORANGE))
        if self.player.shield_time > 0:
            powerups_active.append((f"Shield: {self.player.shield_time // 60}s", CYAN))
        
        for text, color in powerups_active:
            rendered = self.font_tiny.render(text, True, color)
            self.screen.blit(rendered, (20, y_offset))
            y_offset += 25
        
        stats_x = WIDTH - 250
        stats_y = HEIGHT - 105
        overlay4 = pygame.Surface((245, 100))
        overlay4.set_alpha(180)
        overlay4.fill((10, 10, 30))
        self.screen.blit(overlay4, (stats_x, stats_y))
        pygame.draw.rect(self.screen, CYAN, (stats_x, stats_y, 245, 100), 2)
        
        stats_title = self.font_tiny.render("Statistics:", True, WHITE)
        self.screen.blit(stats_title, (stats_x + 10, stats_y + 5))
        
        light_gray = (200, 200, 200)
        stats_texts = [
            f"Games Played: {self.stats.games_played}",
            f"Total Kills: {self.stats.total_kills}",
            f"Bosses Defeated: {self.stats.bosses_defeated}"
        ]
        
        stat_y = stats_y + 30
        for stat in stats_texts:
            text = self.font_mini.render(stat, True, light_gray)
            self.screen.blit(text, (stats_x + 10, stat_y))
            stat_y += 22
    
    def draw_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title_text = self.font_large.render("SPACE SHOOTER", True, CYAN)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 40))
        
        title_shadow = self.font_large.render("SPACE SHOOTER", True, DARK_BLUE)
        self.screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        self.screen.blit(title_text, title_rect)
        
        subtitle = self.font_small.render("Complete Edition", True, GOLD)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 20))
        self.screen.blit(subtitle, subtitle_rect)
        
        y_start = HEIGHT // 2 + 20
        instructions = [
            "CONTROLS:",
            "WASD - Move Ship",
            "Mouse - Aim",
            "F - Toggle Auto-Fire",
            "M - Toggle Sound",
            "ESC - Pause",
            "",
            "Press SPACE to Start",
            "Press ESC to Quit"
        ]
        
        for i, line in enumerate(instructions):
            if line == "CONTROLS:":
                color = CYAN
                font = self.font_small
            elif line == "":
                continue
            elif "Press" in line:
                color = GREEN if "Start" in line else YELLOW
                font = self.font_small
            else:
                color = WHITE
                font = self.font_tiny
            
            text = font.render(line, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, y_start + i * 35))
            self.screen.blit(text, text_rect)
        
        if self.stats.high_score > 0:
            high_score_text = self.font_small.render(f"High Score: {self.stats.high_score}", True, GOLD)
            high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.screen.blit(high_score_text, high_score_rect)
    
    def draw(self):
        self.screen.fill(DARK_BLUE)
        
        for star in self.stars:
            star.draw(self.screen)
        
        if self.show_menu:
            self.draw_menu()
        else:
            for particle in self.particles:
                particle.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            for powerup in self.powerups:
                powerup.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            if self.boss:
                self.boss.draw(self.screen)
            
            self.player.draw(self.screen)
            
            self.draw_ui()
            
            if self.paused:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                pause_text = self.font_large.render("PAUSED", True, CYAN)
                pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)
                
                resume_text = self.font_small.render("Press ESC to Resume", True, WHITE)
                resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
                self.screen.blit(resume_text, resume_rect)
            
            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(220)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                
                game_over_text = self.font_large.render("GAME OVER", True, RED)
                game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
                self.screen.blit(game_over_text, game_over_rect)
                
                final_score = self.font_medium.render(f"Final Score: {self.score}", True, GOLD)
                score_rect = final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(final_score, score_rect)
                
                wave_text = self.font_small.render(f"Wave Reached: {self.wave}", True, CYAN)
                wave_rect = wave_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
                self.screen.blit(wave_text, wave_rect)
                
                if self.score == self.stats.high_score and self.score > 0:
                    new_high = self.font_small.render("NEW HIGH SCORE!", True, GOLD)
                    new_high_rect = new_high.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 110))
                    self.screen.blit(new_high, new_high_rect)
                
                restart_text = self.font_small.render("Press SPACE to Restart", True, GREEN)
                restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 160))
                self.screen.blit(restart_text, restart_rect)
                
                menu_text = self.font_tiny.render("Press ESC for Menu", True, WHITE)
                menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
                self.screen.blit(menu_text, menu_rect)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()