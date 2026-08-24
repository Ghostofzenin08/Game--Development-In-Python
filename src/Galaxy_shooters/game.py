import ctypes
import json
import os
import random
import pygame

try:
    # Set Windows DPI awareness to prevent fullscreen clipping/stretching by OS scaling
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# =====================================================================
# Configuration & Constants
# =====================================================================
WIDTH, HEIGHT = 900, 500
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 75, 55
VEL = 6
BULLET_VEL = 9
MAX_BULLETS = 4
MAX_HEALTH = 10
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 16

POWERUP_SIZE = 28
POWERUP_SPAWN_MS = 6000
POWERUP_DURATION_MS = 7500
AI_VEL = 3
AI_FIRE_INTERVAL_MS = 600

BORDER = pygame.Rect(WIDTH // 2 - 5, 62, 10, HEIGHT - 62)

POWERUP_CONFIG = {
    "rapid": {"label": "RAPID", "icon": "⚡", "color": (90, 220, 255)},
    "shield": {"label": "SHIELD", "icon": "S", "color": (100, 160, 255)},
    "health": {"label": "+HEALTH", "icon": "+", "color": (90, 230, 120)},
    "double": {"label": "DOUBLE", "icon": "2X", "color": (255, 145, 235)},
    "speed": {"label": "SPEED", "icon": "»", "color": (255, 180, 55)},
}

UNLIMITED_CONFIG = {
    "simple": {
        "title": "UNLIMITED SIMPLE",
        "ai_vel": 2,
        "fire_interval_ms": 680,
        "max_health": 8,
        "dodge_chance": 0.25,
    },
    "hard": {
        "title": "UNLIMITED HARD",
        "ai_vel": 4,
        "fire_interval_ms": 400,
        "max_health": 12,
        "dodge_chance": 0.70,
    },
}

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
SOUND_DIR = os.path.join(os.path.dirname(__file__), "assets", "sounds")


# =====================================================================
# Visual Effects Classes
# =====================================================================
class LaserSpriteFactory:
    """Generates glowing laser sprites without requiring pre-baked image assets."""

    @staticmethod
    def create(color: tuple, direction: int) -> pygame.Surface:
        sprite = pygame.Surface((36, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(sprite, (*color, 45), (1, 2, 34, 12))
        pygame.draw.ellipse(sprite, (*color, 115), (5, 4, 27, 8))
        pygame.draw.rect(sprite, (*color, 225), (7, 5, 22, 6), border_radius=3)
        pygame.draw.ellipse(sprite, (255, 255, 255, 255), (10, 6, 17, 4))
        return sprite if direction == 1 else pygame.transform.flip(sprite, True, False)


class MuzzleFlash:
    """Brief expanding light burst at the ship's blaster cannon upon firing."""

    def __init__(self, center: tuple[int, int], color: tuple, direction: int):
        self.center = center
        self.color = color
        self.direction = direction
        self.created_at = pygame.time.get_ticks()
        self.duration_ms = 100

    def is_alive(self, now: int) -> bool:
        return now - self.created_at < self.duration_ms

    def draw(self, surface: pygame.Surface, now: int):
        age = now - self.created_at
        progress = min(1.0, max(0.0, age / self.duration_ms))
        radius = int(15 * (1 - progress)) + 3
        alpha = max(0, min(255, int(230 * (1 - progress))))
        layer = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = (radius * 2, radius * 2)
        pygame.draw.circle(layer, (*self.color, alpha // 3), center, radius * 2)
        pygame.draw.circle(layer, (255, 255, 255, alpha), center, radius)
        surface.blit(layer, layer.get_rect(center=self.center))


class Explosion:
    """Expanding energetic shockwave and particle burst on laser impact."""

    def __init__(self, center: tuple[int, int], color: tuple):
        self.center = center
        self.color = color
        self.created_at = pygame.time.get_ticks()
        self.duration_ms = 360

    def is_alive(self, now: int) -> bool:
        return now - self.created_at < self.duration_ms

    def draw(self, surface: pygame.Surface, now: int):
        age = now - self.created_at
        progress = min(1.0, max(0.0, age / self.duration_ms))
        radius = max(2, int(8 + progress * 32))
        alpha = max(0, min(255, int(255 * (1 - progress))))
        layer = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = (radius * 2, radius * 2)

        pygame.draw.circle(layer, (*self.color, alpha // 3), center, radius + 10)
        pygame.draw.circle(layer, (255, 245, 180, alpha), center, radius, 2)
        for angle in range(0, 360, 60):
            offset_vec = pygame.math.Vector2(1, 0).rotate(angle) * (radius * 1.25)
            offset_x = int(offset_vec.x)
            offset_y = int(offset_vec.y)
            pygame.draw.circle(
                layer,
                (*self.color, alpha),
                (center[0] + offset_x, center[1] + offset_y),
                3,
            )
        surface.blit(layer, layer.get_rect(center=self.center))


class Starfield:
    """Parallax scrolling space starfield background."""

    def __init__(self, width: int, height: int, count: int = 50):
        self.width = width
        self.height = height
        self.stars = [
            [
                random.randint(0, width),
                random.randint(0, height),
                random.uniform(0.5, 2.5),  # speed
                random.randint(1, 3),      # size
                random.randint(140, 255),  # brightness
            ]
            for _ in range(count)
        ]

    def update(self):
        for star in self.stars:
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = self.width
                star[1] = random.randint(0, self.height)

    def draw(self, surface: pygame.Surface):
        for x, y, _, size, alpha in self.stars:
            color = (alpha, alpha, min(255, alpha + 30))
            pygame.draw.circle(surface, color, (int(x), int(y)), size)


class FloatingText:
    """Arcade floating combat text popup that floats upward and fades away."""

    def __init__(self, text: str, x: float, y: float, color: tuple, duration_ms: int = 700):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.created_at = pygame.time.get_ticks()
        self.duration_ms = duration_ms

    def is_alive(self, now: int) -> bool:
        return now - self.created_at < self.duration_ms

    def update(self):
        self.y -= 0.8  # Float up

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, now: int):
        age = now - self.created_at
        progress = age / self.duration_ms
        alpha = max(0, min(255, int(255 * (1 - progress))))

        rendered = font.render(self.text, True, self.color)
        layer = pygame.Surface((rendered.get_width(), rendered.get_height()), pygame.SRCALPHA)
        layer.blit(rendered, (0, 0))
        layer.set_alpha(alpha)
        surface.blit(layer, (self.x - rendered.get_width() // 2, self.y))


class ThrusterParticle:
    """High-quality plasma flame and exhaust particle trail for spaceship thrusters."""

    def __init__(self, x: float, y: float, core_color: tuple, outer_color: tuple, direction: int, boost: bool = False):
        self.x = x
        self.y = y
        self.core_color = core_color
        self.outer_color = outer_color
        self.direction = direction
        self.boost = boost

        mult = 1.6 if boost else 1.0
        self.vel_x = -direction * random.uniform(3.5, 7.5) * mult
        self.vel_y = random.uniform(-1.2, 1.2)
        self.radius = random.uniform(2.5, 4.5)
        self.max_life = random.randint(14, 22)
        self.life = self.max_life

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.radius = min(9.0, self.radius + 0.25)
        self.life -= 1

    def is_alive(self) -> bool:
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        progress = 1.0 - (self.life / self.max_life)  # 0.0 (new) to 1.0 (dead)
        alpha = max(0, min(255, int(240 * (1 - progress))))

        # Dynamic color interpolation over particle lifetime
        if progress < 0.25:
            color = (255, 255, 240)  # Intense hot core
        elif progress < 0.65:
            color = self.core_color
        else:
            color = self.outer_color

        size = max(2, int(self.radius * 2.5))
        layer = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        center = (size, size)

        # Outer glowing flame aura
        pygame.draw.circle(layer, (*color, alpha // 3), center, size)
        # Core intense plasma jet
        pygame.draw.circle(layer, (*color, alpha), center, max(1, size // 2))
        pygame.draw.circle(layer, (255, 255, 255, alpha), center, max(1, size // 4))

        surface.blit(layer, (self.x - size, self.y - size))


# =====================================================================
# Projectile & Collectible Classes
# =====================================================================
class Laser:
    """Laser projectile fired by spaceships."""

    def __init__(self, x: int, y: int, color: tuple, direction: int, sprite: pygame.Surface):
        self.rect = pygame.Rect(x, y, 16, 6)
        self.color = color
        self.direction = direction
        self.sprite = sprite
        self.velocity = BULLET_VEL

    def update(self):
        self.rect.x += self.velocity * self.direction

    def is_offscreen(self, screen_width: int) -> bool:
        return self.rect.x > screen_width or self.rect.right < 0

    def draw(self, surface: pygame.Surface):
        tail_length = 26
        tail = pygame.Rect(
            self.rect.centerx - (tail_length if self.direction == 1 else 0),
            self.rect.centery - 2,
            tail_length,
            4,
        )
        pygame.draw.rect(surface, (*self.color, 55), tail, border_radius=2)
        glow = pygame.Surface((46, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*self.color, 45), (0, 3, 46, 18))
        surface.blit(glow, (self.rect.centerx - 23, self.rect.centery - 12))
        surface.blit(self.sprite, self.sprite.get_rect(center=self.rect.center))


class PowerUp:
    """Floating buff or pickup item with pulsing visual aura."""

    def __init__(self, kind: str, x: int, y: int, created_at: int):
        self.kind = kind
        self.rect = pygame.Rect(x, y, POWERUP_SIZE, POWERUP_SIZE)
        self.created_at = created_at
        self.lifetime_ms = 10000

    @classmethod
    def spawn(cls, border_rect: pygame.Rect, screen_width: int, screen_height: int, now: int) -> "PowerUp":
        kind = random.choice(list(POWERUP_CONFIG.keys()))
        side_x = random.choice(
            (
                random.randint(55, border_rect.left - 55),
                random.randint(border_rect.right + 25, screen_width - 55),
            )
        )
        side_y = random.randint(85, screen_height - 65)
        return cls(kind, side_x, side_y, now)

    def is_expired(self, now: int) -> bool:
        return now - self.created_at > self.lifetime_ms

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, now: int):
        info = POWERUP_CONFIG[self.kind]
        pulse = int(3 * abs((now % 500) / 250 - 1))
        pygame.draw.circle(
            surface,
            (*info["color"], 80),
            self.rect.center,
            self.rect.width // 2 + 5 + pulse,
        )
        pygame.draw.circle(surface, info["color"], self.rect.center, self.rect.width // 2)
        pygame.draw.circle(surface, WHITE, self.rect.center, self.rect.width // 2, 2)
        icon = font.render(info["icon"], True, BLACK)
        surface.blit(icon, icon.get_rect(center=self.rect.center))


# =====================================================================
# Spaceship Entity Class
# =====================================================================
class Spaceship:
    """Represents a player or AI controlled combat spaceship."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        color: tuple,
        image: pygame.Surface,
        laser_sprite: pygame.Surface,
        direction: int,
        boundary_min_x: int,
        boundary_max_x: int,
        controls: dict = None,
        is_ai: bool = False,
    ):
        self.name = name
        self.rect = pygame.Rect(x, y, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
        self.color = color
        self.image = image
        self.laser_sprite = laser_sprite
        self.direction = direction
        self.boundary_min_x = boundary_min_x
        self.boundary_max_x = boundary_max_x
        self.controls = controls or {}
        self.is_ai = is_ai

        self.max_health = MAX_HEALTH
        self.health = MAX_HEALTH
        self.effects: dict[str, int] = {}
        self.last_shot_time = -1000
        self.next_ai_shot_time = 0

    def reset(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y
        self.health = self.max_health
        self.effects.clear()
        self.last_shot_time = -1000
        self.next_ai_shot_time = 0

    def is_effect_active(self, kind: str, now: int) -> bool:
        return self.effects.get(kind, 0) > now

    def apply_powerup(self, kind: str, now: int):
        if kind == "health":
            self.health = min(self.max_health, self.health + 3)
        else:
            self.effects[kind] = now + POWERUP_DURATION_MS

    def get_active_labels(self, now: int) -> list[str]:
        return [
            POWERUP_CONFIG[kind]["label"]
            for kind in ("rapid", "shield", "double", "speed")
            if self.is_effect_active(kind, now)
        ]

    def get_speed(self, now: int) -> int:
        base = AI_VEL if self.is_ai else VEL
        boost = 2 if self.is_ai else 3
        return base + boost if self.is_effect_active("speed", now) else base

    def can_fire(self, current_bullet_count: int, now: int) -> bool:
        rapid = self.is_effect_active("rapid", now)
        cooldown = 110 if rapid else 250
        limit = 6 if rapid else MAX_BULLETS
        return (now - self.last_shot_time >= cooldown) and (current_bullet_count < limit)

    def fire(self, current_bullet_count: int, now: int) -> tuple[list[Laser], MuzzleFlash | None]:
        if not self.can_fire(current_bullet_count, now):
            return [], None

        rapid = self.is_effect_active("rapid", now)
        limit = 6 if rapid else MAX_BULLETS
        offsets = (-9, 9) if self.is_effect_active("double", now) else (0,)

        new_bullets = []
        for offset in offsets:
            if current_bullet_count + len(new_bullets) >= limit:
                break
            x = self.rect.right - 2 if self.direction == 1 else self.rect.left - 14
            new_bullets.append(
                Laser(
                    x,
                    self.rect.centery - 3 + offset,
                    self.color,
                    self.direction,
                    self.laser_sprite,
                )
            )

        flash_center = (
            self.rect.right if self.direction == 1 else self.rect.left,
            self.rect.centery,
        )
        flash = MuzzleFlash(flash_center, self.color, self.direction)
        self.last_shot_time = now
        return new_bullets, flash

    def take_damage(self, now: int, amount: int = 1) -> bool:
        """Inflicts damage unless shielded. Returns True if damage was taken."""
        if self.is_effect_active("shield", now):
            return False
        self.health = max(0, self.health - amount)
        return True

    def move_human(self, keys_pressed, now: int, screen_height: int):
        speed = self.get_speed(now)
        if self.controls.get("left") and keys_pressed[self.controls["left"]]:
            if self.rect.x - speed > self.boundary_min_x:
                self.rect.x -= speed
        if self.controls.get("right") and keys_pressed[self.controls["right"]]:
            if self.rect.x + speed + self.rect.width < self.boundary_max_x:
                self.rect.x += speed
        if self.controls.get("up") and keys_pressed[self.controls["up"]]:
            if self.rect.y - speed > 60:
                self.rect.y -= speed
        if self.controls.get("down") and keys_pressed[self.controls["down"]]:
            if self.rect.y + speed + self.rect.height < screen_height - 15:
                self.rect.y += speed

    def update_ai(
        self,
        target_ship: "Spaceship",
        incoming_bullets: list[Laser],
        powerups: list[PowerUp],
        now: int,
        border_rect: pygame.Rect,
        screen_height: int,
        dodge_chance: float = 0.5,
        override_speed: int = 3,
    ):
        """Pursues opponent, dodges incoming fire, and collects available powerups."""
        target_y = target_ship.rect.centery

        # Dodge the nearest dangerous laser heading toward the ship (with human reaction window)
        threats = [b for b in incoming_bullets if b.rect.x < self.rect.left]
        if threats and random.random() < dodge_chance:
            threat = max(threats, key=lambda b: b.rect.x)
            if abs(threat.rect.centery - self.rect.centery) < 75:
                target_y = 90 if threat.rect.centery > self.rect.centery else screen_height - 70
        else:
            ai_pickups = [p for p in powerups if p.rect.centerx > border_rect.right]
            if ai_pickups:
                target_y = min(
                    ai_pickups,
                    key=lambda p: abs(p.rect.centery - self.rect.centery),
                ).rect.centery

        speed = override_speed + (2 if self.is_effect_active("speed", now) else 0)
        if self.rect.centery < target_y - 10 and self.rect.bottom + speed < screen_height - 15:
            self.rect.y += speed
        elif self.rect.centery > target_y + 10 and self.rect.top - speed > 60:
            self.rect.y -= speed

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        now: int,
        is_hit_feedback: bool,
    ):
        surface.blit(self.image, (self.rect.x, self.rect.y))

        # Shield glow overlay
        if self.is_effect_active("shield", now):
            pygame.draw.ellipse(surface, (110, 185, 255), self.rect.inflate(18, 18), 2)

        # Hit indicator
        if is_hit_feedback:
            pygame.draw.rect(surface, WHITE, self.rect.inflate(12, 12), 3)
            hit_text = font.render("HIT!", True, WHITE)
            surface.blit(
                hit_text,
                (
                    self.rect.centerx - hit_text.get_width() // 2,
                    self.rect.y - hit_text.get_height() - 8,
                ),
            )


# =====================================================================
# Audio Manager
# =====================================================================
class AudioManager:
    """Manages game audio, sound effects, and background music playback."""

    def __init__(self):
        self.sound_enabled = True
        self.laser_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "laser_GS.mp3"))
        self.hit_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "damage_GS.mp3"))
        self.victory_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "victory_GS.mp3"))
        self.victory_sound.set_volume(1.0)
        self.victory_channel = pygame.mixer.Channel(0)
        self.bg_music_path = os.path.join(SOUND_DIR, "background_GS.mp3")

    def set_enabled(self, enabled: bool):
        self.sound_enabled = enabled
        if not enabled:
            pygame.mixer.music.pause()
            pygame.mixer.stop()
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                self.play_music()

    def play_music(self):
        if not self.sound_enabled:
            return
        try:
            pygame.mixer.music.load(self.bg_music_path)
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def fadeout_music(self, ms: int = 250):
        try:
            pygame.mixer.music.fadeout(ms)
        except Exception:
            pass

    def play_laser(self, enabled: bool = True):
        if self.sound_enabled and enabled:
            self.laser_sound.play()

    def play_hit(self, enabled: bool = True):
        if self.sound_enabled and enabled:
            self.hit_sound.play()

    def play_victory(self, enabled: bool = True):
        if self.sound_enabled and enabled:
            self.victory_channel.play(self.victory_sound)


# =====================================================================
# Main Game Controller Class
# =====================================================================
class GalaxyShootersGame:
    """High-level game coordinator handling states, game loop, physics, and rendering."""

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.is_fullscreen = True
        try:
            self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        except Exception:
            try:
                self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
            except Exception:
                try:
                    info = pygame.display.Info()
                    self.window = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                except Exception:
                    self.is_fullscreen = False
                    self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Galaxy Shooters")
        self.clock = pygame.time.Clock()

        # Fonts
        self.health_font = pygame.font.SysFont("comicsans", 30)
        self.health_small_font = pygame.font.SysFont("comicsans", 20)
        self.title_font = pygame.font.SysFont("comicsans", 52)
        self.menu_font = pygame.font.SysFont("comicsans", 32)
        self.powerup_font = pygame.font.SysFont("arial", 17, bold=True)

        # Asset loading
        google_icon_path = os.path.join(ASSET_DIR, "google_icon.png")
        if os.path.exists(google_icon_path):
            self.google_icon_raw = pygame.image.load(google_icon_path)
            pygame.display.set_icon(self.google_icon_raw)
            self.google_icon_badge = pygame.transform.scale(self.google_icon_raw, (44, 44))
        else:
            self.google_icon_badge = None

        self.bg_space = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "background_GS.png")),
            (WIDTH, HEIGHT),
        )

        yellow_raw = pygame.image.load(os.path.join(ASSET_DIR, "yellow_spaceship.png"))
        self.yellow_img = pygame.transform.rotate(
            pygame.transform.scale(yellow_raw, (SPACESHIP_HEIGHT, SPACESHIP_WIDTH)),
            90,
        )

        red_raw = pygame.image.load(os.path.join(ASSET_DIR, "red_spaceship.png"))
        self.red_img = pygame.transform.rotate(
            pygame.transform.scale(red_raw, (SPACESHIP_HEIGHT, SPACESHIP_WIDTH)),
            270,
        )

        self.yellow_laser_sprite = LaserSpriteFactory.create(YELLOW, 1)
        self.red_laser_sprite = LaserSpriteFactory.create(RED, -1)

        self.audio = AudioManager()

        # Game Entities
        self.yellow = Spaceship(
            name="yellow",
            x=100,
            y=300,
            color=YELLOW,
            image=self.yellow_img,
            laser_sprite=self.yellow_laser_sprite,
            direction=1,
            boundary_min_x=0,
            boundary_max_x=BORDER.x,
            controls={
                "left": pygame.K_a,
                "right": pygame.K_d,
                "up": pygame.K_w,
                "down": pygame.K_s,
                "fire": pygame.K_SPACE,
            },
            is_ai=False,
        )

        self.red = Spaceship(
            name="red",
            x=700,
            y=300,
            color=RED,
            image=self.red_img,
            laser_sprite=self.red_laser_sprite,
            direction=-1,
            boundary_min_x=BORDER.x + BORDER.width,
            boundary_max_x=WIDTH,
            controls={
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "fire": pygame.K_RCTRL,
            },
            is_ai=True,
        )

        self.yellow_bullets: list[Laser] = []
        self.red_bullets: list[Laser] = []
        self.flashes: list[MuzzleFlash] = []
        self.explosions: list[Explosion] = []
        self.powerups: list[PowerUp] = []
        self.floating_texts: list[FloatingText] = []
        self.thruster_particles: list[ThrusterParticle] = []
        self.starfield = Starfield(WIDTH, HEIGHT, count=55)

        # High Score & Unlimited State
        self.highscore_file = os.path.join(os.path.dirname(__file__), "highscores_gs.json")
        self.score = 0
        self.high_score = self.load_high_score()
        self.difficulty = "simple"  # 'simple' or 'hard'
        self.wave_count = 1

        # Screen Shake
        self.shake_amount = 0
        self.shake_until = 0

        # Game State & Navigation
        self.running = True
        self.game_mode = "ai"
        self.state = "menu"  # 'menu', 'playing', 'game_over', 'level_clear'
        self.is_paused = False
        self.sound_enabled = True
        self.winner_text = ""
        self.hit_player = None
        self.hit_feedback_until = 0
        self.next_powerup_spawn = 0

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        try:
            if self.is_fullscreen:
                self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
            else:
                self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
        except Exception:
            try:
                if self.is_fullscreen:
                    self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                else:
                    self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
            except Exception:
                pass

    def load_high_score(self) -> int:
        try:
            if os.path.exists(self.highscore_file):
                with open(self.highscore_file, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except Exception:
            pass
        return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
        try:
            with open(self.highscore_file, "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def trigger_shake(self, amount: int = 8, duration_ms: int = 200, now: int = 0):
        self.shake_amount = amount
        self.shake_until = now + duration_ms

    def apply_level_config(self):
        cfg = UNLIMITED_CONFIG.get(self.difficulty, UNLIMITED_CONFIG["simple"])
        health_bonus = (self.wave_count - 1) * 2
        self.yellow.health = self.yellow.max_health
        self.yellow.rect.x = 100
        self.yellow.rect.y = 300
        self.red.max_health = cfg["max_health"] + health_bonus
        self.red.health = self.red.max_health
        self.red.rect.x = 700
        self.red.rect.y = 300
        self.yellow.effects.clear()
        self.red.effects.clear()
        self.yellow_bullets.clear()
        self.red_bullets.clear()
        self.powerups.clear()
        self.flashes.clear()
        self.explosions.clear()

    def reset_match(self):
        now = pygame.time.get_ticks()
        self.wave_count = 1
        self.score = 0
        self.yellow.reset(100, 300)
        self.red.reset(700, 300)
        self.red.is_ai = (self.game_mode == "ai")
        self.apply_level_config()
        self.flashes.clear()
        self.explosions.clear()
        self.floating_texts.clear()
        self.thruster_particles.clear()
        self.shake_amount = 0
        self.shake_until = 0
        self.hit_player = None
        self.hit_feedback_until = 0
        self.winner_text = ""
        self.next_powerup_spawn = now + POWERUP_SPAWN_MS
        self.audio.play_music()
        self.state = "playing"

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.audio.set_enabled(self.sound_enabled)

    def handle_events(self, now: int):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_high_score()
                self.running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    mx, my = event.pos
                    
                    if self.state == "menu":
                        btn_mode_container = pygame.Rect(WIDTH // 2 - 190, 140, 380, 85)
                        btn_simple = pygame.Rect(WIDTH // 2 - 175, 182, 160, 34)
                        btn_hard = pygame.Rect(WIDTH // 2 + 15, 182, 160, 34)
                        btn_two = pygame.Rect(WIDTH // 2 - 190, 242, 380, 48)
                        btn_start = pygame.Rect(WIDTH // 2 - 190, 308, 380, 54)
                        btn_quit = pygame.Rect(WIDTH // 2 - 190, 378, 380, 44)

                        if btn_simple.collidepoint(mx, my):
                            self.difficulty = "simple"
                            self.game_mode = "ai"
                            self.reset_match()
                        elif btn_hard.collidepoint(mx, my):
                            self.difficulty = "hard"
                            self.game_mode = "ai"
                            self.reset_match()
                        elif btn_mode_container.collidepoint(mx, my):
                            self.game_mode = "ai"
                            self.reset_match()
                        elif btn_two.collidepoint(mx, my):
                            self.floating_texts.append(FloatingText("2-PLAYER MODE COMING SOON!", WIDTH // 2, 255, (255, 215, 0), duration_ms=1800))
                        elif btn_start.collidepoint(mx, my):
                            self.reset_match()
                        elif btn_quit.collidepoint(mx, my):
                            self.save_high_score()
                            self.running = False

                    elif self.state == "game_over":
                        btn_restart = pygame.Rect(WIDTH // 2 - 160, 280, 320, 48)
                        btn_menu = pygame.Rect(WIDTH // 2 - 160, 345, 320, 48)
                        if btn_restart.collidepoint(mx, my):
                            self.reset_match()
                        elif btn_menu.collidepoint(mx, my):
                            self.state = "menu"

                    elif self.state == "playing":
                        btn_nav = pygame.Rect(WIDTH - 125, 12, 110, 34)
                        if btn_nav.collidepoint(mx, my):
                            self.is_paused = not self.is_paused
                        elif self.is_paused:
                            btn_resume = pygame.Rect(WIDTH // 2 - 150, 160, 300, 42)
                            btn_restart = pygame.Rect(WIDTH // 2 - 150, 215, 300, 42)
                            btn_sound = pygame.Rect(WIDTH // 2 - 150, 270, 300, 42)
                            btn_screen = pygame.Rect(WIDTH // 2 - 150, 325, 300, 42)
                            btn_menu = pygame.Rect(WIDTH // 2 - 150, 380, 300, 42)
                            if btn_resume.collidepoint(mx, my):
                                self.is_paused = False
                            elif btn_restart.collidepoint(mx, my):
                                self.apply_level_config()
                                self.is_paused = False
                            elif btn_sound.collidepoint(mx, my):
                                self.toggle_sound()
                            elif btn_screen.collidepoint(mx, my):
                                self.toggle_fullscreen()
                            elif btn_menu.collidepoint(mx, my):
                                self.save_high_score()
                                self.state = "menu"
                                self.is_paused = False
                        else:
                            bullets, flash = self.yellow.fire(len(self.yellow_bullets), now)
                            if bullets:
                                self.yellow_bullets.extend(bullets)
                                self.flashes.append(flash)
                                self.audio.play_laser(self.sound_enabled)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11 or (event.key == pygame.K_f and (pygame.key.get_mods() & pygame.KMOD_ALT)):
                    self.toggle_fullscreen()

                if self.is_paused:
                    if event.key == pygame.K_s:
                        self.toggle_sound()
                    elif event.key == pygame.K_m:
                        self.save_high_score()
                        self.state = "menu"
                        self.is_paused = False

                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.game_mode = "ai"
                    elif event.key == pygame.K_2:
                        self.floating_texts.append(FloatingText("2-PLAYER MODE COMING SOON!", WIDTH // 2, 255, (255, 215, 0), duration_ms=1800))
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_match()
                    elif event.key == pygame.K_ESCAPE:
                        self.save_high_score()
                        self.running = False

                elif self.state == "playing":
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.is_paused = not self.is_paused
                    elif not self.is_paused:
                        # Yellow Fire Trigger
                        if event.key == self.yellow.controls.get("fire"):
                            bullets, flash = self.yellow.fire(len(self.yellow_bullets), now)
                            if bullets:
                                self.yellow_bullets.extend(bullets)
                                self.flashes.append(flash)
                                self.audio.play_laser(self.sound_enabled)

                    # Red Fire Trigger (Human mode)
                    if (
                        self.game_mode == "two"
                        and event.key == self.red.controls.get("fire")
                    ):
                        bullets, flash = self.red.fire(len(self.red_bullets), now)
                        if bullets:
                            self.red_bullets.extend(bullets)
                            self.flashes.append(flash)
                            self.audio.play_laser(self.sound_enabled)

                    if event.key == pygame.K_ESCAPE:
                        self.save_high_score()
                        self.state = "menu"
                        self.audio.fadeout_music()

                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.reset_match()
                    elif event.key == pygame.K_ESCAPE:
                        self.save_high_score()
                        self.state = "menu"

    def update_physics_and_ai(self, now: int):
        if self.is_paused:
            return

        keys = pygame.key.get_pressed()

        # Mouse position tracking (only when mouse actively moves)
        mx, my = pygame.mouse.get_pos()
        rel_x, rel_y = pygame.mouse.get_rel()
        if pygame.mouse.get_focused() and (rel_x != 0 or rel_y != 0):
            self.yellow.rect.centerx = max(45, min(BORDER.x - 45, mx))
            self.yellow.rect.centery = max(90, min(HEIGHT - 40, my))

        # Keyboard fallback/override movement
        self.yellow.move_human(keys, now, HEIGHT)

        # Mouse click continuous stream / rapid fire holding
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # Left mouse button held
            bullets, flash = self.yellow.fire(len(self.yellow_bullets), now)
            if bullets:
                self.yellow_bullets.extend(bullets)
                self.flashes.append(flash)
                self.audio.play_laser(self.sound_enabled)

        if self.game_mode == "ai":
            cfg = UNLIMITED_CONFIG.get(self.difficulty, UNLIMITED_CONFIG["simple"])
            self.red.update_ai(
                self.yellow,
                self.yellow_bullets,
                self.powerups,
                now,
                BORDER,
                HEIGHT,
                dodge_chance=cfg["dodge_chance"],
                override_speed=cfg["ai_vel"],
            )
            # AI automatic firing logic
            if now >= self.red.next_ai_shot_time:
                bullets, flash = self.red.fire(len(self.red_bullets), now)
                if bullets:
                    self.red_bullets.extend(bullets)
                    self.flashes.append(flash)
                    self.audio.play_laser(self.sound_enabled)
                self.red.next_ai_shot_time = now + cfg["fire_interval_ms"]
        else:
            self.red.move_human(keys, now, HEIGHT)

        # Rapid Fire continuous stream while holding fire key
        if self.yellow.is_effect_active("rapid", now) and keys[self.yellow.controls["fire"]]:
            bullets, flash = self.yellow.fire(len(self.yellow_bullets), now)
            if bullets:
                self.yellow_bullets.extend(bullets)
                self.flashes.append(flash)
                self.audio.play_laser(self.sound_enabled)

        # Update starfield background
        self.starfield.update()

        # Generate high-quality dual thruster engine plumes
        for ship, core_clr, outer_clr, dir_x in [
            (self.yellow, (255, 185, 30), (235, 70, 20), 1),
            (self.red, (255, 60, 90), (160, 20, 90), -1),
        ]:
            is_boost = ship.is_effect_active("speed", now)
            spawn_x = ship.rect.left - 2 if dir_x == 1 else ship.rect.right + 2
            for offset_y in (-12, 12):
                if random.random() < (0.95 if is_boost else 0.75):
                    self.thruster_particles.append(
                        ThrusterParticle(
                            spawn_x,
                            ship.rect.centery + offset_y,
                            core_clr,
                            outer_clr,
                            dir_x,
                            boost=is_boost,
                        )
                    )

        for tp in self.thruster_particles[:]:
            tp.update()
            if not tp.is_alive():
                self.thruster_particles.remove(tp)

        # PowerUp Spawning & Lifecycles
        if now >= self.next_powerup_spawn:
            self.powerups.append(PowerUp.spawn(BORDER, WIDTH, HEIGHT, now))
            self.next_powerup_spawn = now + POWERUP_SPAWN_MS

        for pickup in self.powerups[:]:
            if pickup.is_expired(now):
                self.powerups.remove(pickup)
            elif self.yellow.rect.colliderect(pickup.rect):
                label = POWERUP_CONFIG[pickup.kind]["label"]
                self.yellow.apply_powerup(pickup.kind, now)
                self.powerups.remove(pickup)
                self.score += 150
                self.floating_texts.append(FloatingText(f"+{label}!", self.yellow.rect.centerx, self.yellow.rect.top - 10, (90, 230, 255)))
            elif self.red.rect.colliderect(pickup.rect):
                label = POWERUP_CONFIG[pickup.kind]["label"]
                self.red.apply_powerup(pickup.kind, now)
                self.powerups.remove(pickup)
                self.floating_texts.append(FloatingText(f"+{label}!", self.red.rect.centerx, self.red.rect.top - 10, (255, 140, 140)))

        # Bullets movement & collisions
        for bullet in self.yellow_bullets[:]:
            bullet.update()
            if self.red.rect.colliderect(bullet.rect):
                self.yellow_bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.rect.center, YELLOW))
                took_damage = self.red.take_damage(now)
                self.hit_player = "red"
                self.hit_feedback_until = now + 250
                if self.sound_enabled:
                    self.audio.play_hit()
                self.trigger_shake(amount=9, duration_ms=220, now=now)
                if took_damage:
                    self.score += 100
                txt = "HIT!" if took_damage else "SHIELDED!"
                clr = (255, 90, 90) if took_damage else (100, 180, 255)
                self.floating_texts.append(FloatingText(txt, self.red.rect.centerx, self.red.rect.top - 15, clr))
            elif bullet.is_offscreen(WIDTH):
                self.yellow_bullets.remove(bullet)

        for bullet in self.red_bullets[:]:
            bullet.update()
            if self.yellow.rect.colliderect(bullet.rect):
                self.red_bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.rect.center, RED))
                took_damage = self.yellow.take_damage(now)
                self.hit_player = "yellow"
                self.hit_feedback_until = now + 250
                if self.sound_enabled:
                    self.audio.play_hit()
                self.trigger_shake(amount=9, duration_ms=220, now=now)
                txt = "HIT!" if took_damage else "SHIELDED!"
                clr = (255, 240, 90) if took_damage else (100, 180, 255)
                self.floating_texts.append(FloatingText(txt, self.yellow.rect.centerx, self.yellow.rect.top - 15, clr))
            elif bullet.is_offscreen(WIDTH):
                self.red_bullets.remove(bullet)

        # Clean up floating text & visual effects
        for ft in self.floating_texts[:]:
            ft.update()
            if not ft.is_alive(now):
                self.floating_texts.remove(ft)

        self.flashes = [f for f in self.flashes if f.is_alive(now)]
        self.explosions = [e for e in self.explosions if e.is_alive(now)]

        if self.state == "level_clear":
            if now >= getattr(self, "level_clear_until", 0):
                self.apply_level_config()
                self.state = "playing"
            return

        # Check win/loss/level conditions
        if self.red.health <= 0:
            self.score += 500 * self.wave_count
            self.save_high_score()
            self.wave_count += 1
            self.state = "level_clear"
            self.level_clear_until = now + 2000
            if self.sound_enabled:
                self.audio.play_victory()
            self.trigger_shake(amount=14, duration_ms=350, now=now)
        elif self.yellow.health <= 0:
            self.winner_text = "GAME OVER!"
            self.state = "game_over"
            self.save_high_score()
            self.trigger_shake(amount=18, duration_ms=450, now=now)
            self.audio.fadeout_music(250)

    def draw_health_bar(self, surface: pygame.Surface, x: int, y: int, health: int, max_health: int, color: tuple, align_right: bool = False):
        health_ratio = max(0, health) / max(1, max_health)
        if health_ratio > 0.6:
            state_color = (70, 220, 90)
        elif health_ratio > 0.3:
            state_color = (245, 190, 45)
        elif health_ratio > 0:
            state_color = (235, 70, 55)
        else:
            state_color = (80, 80, 80)

        bar_x = x - HEALTH_BAR_WIDTH if align_right else x
        background = pygame.Rect(bar_x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
        fill = pygame.Rect(bar_x, y, int(HEALTH_BAR_WIDTH * health_ratio), HEALTH_BAR_HEIGHT)
        pygame.draw.rect(surface, BLACK, background, border_radius=3)
        pygame.draw.rect(surface, state_color, fill, border_radius=3)
        pygame.draw.rect(surface, WHITE, background, 2, border_radius=3)

        health_text = self.health_small_font.render(f"{max(0, health)}/{max_health}", True, WHITE)
        text_x = bar_x + HEALTH_BAR_WIDTH - health_text.get_width() - 2 if align_right else bar_x + 2
        text_y = max(1, y - health_text.get_height() + 2)
        surface.blit(health_text, (text_x, text_y))

    def draw_hud(self, surface: pygame.Surface, now: int):
        # Draw translucent dark top HUD bar background
        hud_bg = pygame.Surface((WIDTH, 58), pygame.SRCALPHA)
        hud_bg.fill((10, 10, 25, 210))
        surface.blit(hud_bg, (0, 0))

        # Health bars
        self.draw_health_bar(surface, 15, 20, self.yellow.health, self.yellow.max_health, YELLOW)
        self.draw_health_bar(surface, WIDTH - 140, 20, self.red.health, self.red.max_health, RED, align_right=True)

        # Level Title & Score HUD
        if self.game_mode == "two":
            lvl_title = "LOCAL 2-PLAYER BATTLE ARENA"
        else:
            lvl_title = f"UNLIMITED WAVE {self.wave_count} - {self.difficulty.upper()}"
        lvl_surface = self.health_small_font.render(lvl_title, True, (255, 215, 0))
        surface.blit(lvl_surface, (WIDTH // 2 - lvl_surface.get_width() // 2, 6))

        score_surface = self.health_small_font.render(f"SCORE: {self.score}   HIGH SCORE: {self.high_score}", True, WHITE)
        surface.blit(score_surface, (WIDTH // 2 - score_surface.get_width() // 2, 30))

        # Active powerup status texts
        yellow_active = self.yellow.get_active_labels(now)
        if yellow_active:
            text = self.powerup_font.render(" | ".join(yellow_active), True, WHITE)
            surface.blit(text, (15, 38))

        red_active = self.red.get_active_labels(now)
        if red_active:
            text = self.powerup_font.render(" | ".join(red_active), True, WHITE)
            surface.blit(text, (WIDTH - 140 - text.get_width(), 38))

        # In-Game Navigation & Pause Button
        mx, my = pygame.mouse.get_pos()
        btn_nav = pygame.Rect(WIDTH - 125, 12, 110, 34)
        is_hovered = btn_nav.collidepoint(mx, my)
        
        nav_bg = pygame.Surface((btn_nav.width, btn_nav.height), pygame.SRCALPHA)
        nav_bg.fill((66, 133, 244, 210) if is_hovered else (25, 30, 60, 180))
        surface.blit(nav_bg, (btn_nav.x, btn_nav.y))
        
        border_clr = (255, 215, 0) if is_hovered else (80, 120, 200)
        pygame.draw.rect(surface, border_clr, btn_nav, 2, border_radius=8)

        nav_txt = self.health_small_font.render("NAV / PAUSE", True, WHITE)
        surface.blit(nav_txt, (btn_nav.centerx - nav_txt.get_width() // 2, btn_nav.centery - nav_txt.get_height() // 2))

    def draw_pause_navigation_menu(self, surface: pygame.Surface):
        mx, my = pygame.mouse.get_pos()

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 30, 210))
        surface.blit(overlay, (0, 0))

        # Title Header
        title = self.title_font.render("GEAR NAVIGATION", True, (255, 215, 0))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 95))

        subtitle = self.health_small_font.render("IN-GAME CONTROLS & BATTLE NAVIGATION", True, (90, 220, 255))
        surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 145))

        # Action Buttons
        btn_resume = pygame.Rect(WIDTH // 2 - 150, 160, 300, 42)
        btn_restart = pygame.Rect(WIDTH // 2 - 150, 215, 300, 42)
        btn_sound = pygame.Rect(WIDTH // 2 - 150, 270, 300, 42)
        btn_screen = pygame.Rect(WIDTH // 2 - 150, 325, 300, 42)
        btn_menu = pygame.Rect(WIDTH // 2 - 150, 380, 300, 42)

        sound_label = "S  SOUND: ON" if self.sound_enabled else "S  SOUND: OFF"
        screen_label = "F11  FULLSCREEN: ON" if self.is_fullscreen else "F11  FULLSCREEN: OFF"
        options = [
            (btn_resume, "> RESUME BATTLE <"),
            (btn_restart, "R  RESTART LEVEL"),
            (btn_sound, sound_label),
            (btn_screen, screen_label),
            (btn_menu, "M  MAIN MENU"),
        ]

        for rect, label in options:
            is_hover = rect.collidepoint(mx, my)
            card = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            card.fill((66, 133, 244, 230) if is_hover else (18, 22, 45, 220))
            pygame.draw.rect(card, (66, 133, 244, 230) if is_hover else (18, 22, 45, 220), (0, 0, rect.width, rect.height), border_radius=10)
            surface.blit(card, (rect.x, rect.y))

            border_clr = (255, 215, 0) if is_hover else (70, 110, 190)
            pygame.draw.rect(surface, border_clr, rect, 3 if is_hover else 2, border_radius=10)

            txt = self.health_small_font.render(label, True, (255, 235, 90) if is_hover else WHITE)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

    def draw_menu(self, surface: pygame.Surface):
        surface.blit(self.bg_space, (0, 0))
        mx, my = pygame.mouse.get_pos()

        # Title Header
        title_text = self.title_font.render("GALAXY SHOOTERS", True, WHITE)
        surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 35))

        subtitle_text = self.health_small_font.render("UNLIMITED BATTLE ARENA", True, (90, 220, 255))
        surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 98))

        # Card 1: Unlimited Mode Container Card
        btn_mode_container = pygame.Rect(WIDTH // 2 - 190, 138, 380, 86)
        is_h_container = btn_mode_container.collidepoint(mx, my)

        card1 = pygame.Surface((btn_mode_container.width, btn_mode_container.height), pygame.SRCALPHA)
        card1.fill((22, 32, 65, 200))
        pygame.draw.rect(card1, (22, 32, 65, 200), (0, 0, btn_mode_container.width, btn_mode_container.height), border_radius=14)
        surface.blit(card1, (btn_mode_container.x, btn_mode_container.y))
        
        border_clr = (255, 215, 0) if is_h_container else (65, 105, 185)
        pygame.draw.rect(surface, border_clr, btn_mode_container, 2, border_radius=14)

        # Title inside Card 1
        txt1 = self.health_small_font.render("1. UNLIMITED ENDLESS BATTLE", True, (255, 235, 90))
        surface.blit(txt1, (btn_mode_container.centerx - txt1.get_width() // 2, 148))

        # Sub-toggles inside Card 1
        btn_simple = pygame.Rect(WIDTH // 2 - 175, 180, 160, 34)
        btn_hard = pygame.Rect(WIDTH // 2 + 15, 180, 160, 34)

        for r, label, is_act in [
            (btn_simple, "SIMPLE (EASY)", self.difficulty == "simple" and self.game_mode == "ai"),
            (btn_hard, "HARD (INTENSE)", self.difficulty == "hard" and self.game_mode == "ai"),
        ]:
            is_h = r.collidepoint(mx, my)
            sub_card = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            bg_clr = (40, 160, 240, 230) if is_h else ((25, 130, 60, 210) if is_act and "SIMPLE" in label else ((160, 40, 40, 210) if is_act else (15, 20, 35, 170)))
            sub_card.fill(bg_clr)
            pygame.draw.rect(sub_card, bg_clr, (0, 0, r.width, r.height), border_radius=8)
            surface.blit(sub_card, (r.x, r.y))
            
            b_clr = (255, 215, 0) if (is_act or is_h) else (70, 90, 140)
            pygame.draw.rect(surface, b_clr, r, 2 if (is_act or is_h) else 1, border_radius=8)
            
            t_clr = WHITE if (is_act or is_h) else (170, 180, 200)
            stxt = self.health_small_font.render(label, True, t_clr)
            surface.blit(stxt, (r.centerx - stxt.get_width() // 2, r.centery - stxt.get_height() // 2))

        # Card 2: 2 Players PVP (Coming Soon)
        btn_two = pygame.Rect(WIDTH // 2 - 190, 240, 380, 48)
        is_h_two = btn_two.collidepoint(mx, my)

        card2 = pygame.Surface((btn_two.width, btn_two.height), pygame.SRCALPHA)
        card2.fill((30, 35, 55, 160))
        pygame.draw.rect(card2, (30, 35, 55, 160), (0, 0, btn_two.width, btn_two.height), border_radius=12)
        surface.blit(card2, (btn_two.x, btn_two.y))
        
        pygame.draw.rect(surface, (255, 215, 0) if is_h_two else (75, 80, 105), btn_two, 2 if is_h_two else 1, border_radius=12)
        
        txt2 = self.health_small_font.render("2. 2 PLAYERS PVP   [ COMING SOON ]", True, (160, 170, 190))
        surface.blit(txt2, (btn_two.centerx - txt2.get_width() // 2, btn_two.centery - txt2.get_height() // 2))

        # Card 3: Start Battle Button
        btn_start = pygame.Rect(WIDTH // 2 - 190, 306, 380, 54)
        is_h_start = btn_start.collidepoint(mx, my)

        card3 = pygame.Surface((btn_start.width, btn_start.height), pygame.SRCALPHA)
        card3.fill((66, 133, 244, 230) if is_h_start else (20, 65, 140, 190))
        pygame.draw.rect(card3, (66, 133, 244, 230) if is_h_start else (20, 65, 140, 190), (0, 0, btn_start.width, btn_start.height), border_radius=12)
        surface.blit(card3, (btn_start.x, btn_start.y))
        
        pygame.draw.rect(surface, (255, 215, 0) if is_h_start else (70, 130, 220), btn_start, 3 if is_h_start else 2, border_radius=12)
        
        txt3 = self.health_small_font.render("> START UNLIMITED BATTLE <", True, (255, 235, 90) if is_h_start else WHITE)
        surface.blit(txt3, (btn_start.centerx - txt3.get_width() // 2, btn_start.centery - txt3.get_height() // 2))

        # Card 4: Exit Button
        btn_quit = pygame.Rect(WIDTH // 2 - 190, 376, 380, 44)
        is_h_quit = btn_quit.collidepoint(mx, my)

        card4 = pygame.Surface((btn_quit.width, btn_quit.height), pygame.SRCALPHA)
        card4.fill((180, 40, 40, 210) if is_h_quit else (18, 22, 40, 150))
        pygame.draw.rect(card4, (180, 40, 40, 210) if is_h_quit else (18, 22, 40, 150), (0, 0, btn_quit.width, btn_quit.height), border_radius=12)
        surface.blit(card4, (btn_quit.x, btn_quit.y))
        
        pygame.draw.rect(surface, (255, 90, 90) if is_h_quit else (80, 85, 110), btn_quit, 2 if is_h_quit else 1, border_radius=12)
        
        txt4 = self.health_small_font.render("X  EXIT GAME", True, WHITE)
        surface.blit(txt4, (btn_quit.centerx - txt4.get_width() // 2, btn_quit.centery - txt4.get_height() // 2))

        # Floating text notifications
        for ft in self.floating_texts:
            ft.draw(surface, self.powerup_font, pygame.time.get_ticks())

        controls_text = self.health_small_font.render(
            "Select SIMPLE or HARD difficulty | WASD or Mouse to move | Click / Space to shoot",
            True,
            (180, 210, 255),
        )
        surface.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 442))

    def draw_winner(self, surface: pygame.Surface):
        surface.blit(self.bg_space, (0, 0))
        mx, my = pygame.mouse.get_pos()

        winner_text = self.title_font.render(self.winner_text, True, (255, 215, 0))
        surface.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 135))

        score_text = self.health_font.render(f"FINAL SCORE: {self.score}   HIGH SCORE: {self.high_score}", True, WHITE)
        surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 205))

        btn_restart = pygame.Rect(WIDTH // 2 - 160, 280, 320, 48)
        btn_menu = pygame.Rect(WIDTH // 2 - 160, 345, 320, 48)

        for rect, label in [(btn_restart, "> PLAY AGAIN <"), (btn_menu, "< MAIN MENU")]:
            is_hovered = rect.collidepoint(mx, my)
            card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bg_color = (66, 133, 244, 220) if is_hovered else (18, 22, 40, 160)
            card_surface.fill(bg_color)
            pygame.draw.rect(card_surface, bg_color, (0, 0, rect.width, rect.height), border_radius=10)
            surface.blit(card_surface, (rect.x, rect.y))

            border_color = (255, 215, 0) if is_hovered else (70, 110, 180)
            pygame.draw.rect(surface, border_color, rect, 3 if is_hovered else 2, border_radius=10)

            btn_txt = self.health_small_font.render(label, True, WHITE)
            surface.blit(btn_txt, (rect.centerx - btn_txt.get_width() // 2, rect.centery - btn_txt.get_height() // 2))

    def draw_level_clear(self, surface: pygame.Surface):
        surface.blit(self.bg_space, (0, 0))
        self.starfield.draw(surface)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 35, 200))
        surface.blit(overlay, (0, 0))

        title = self.title_font.render(f"WAVE {self.wave_count - 1} CLEARED!", True, (255, 215, 0))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))

        bonus = self.menu_font.render(f"+{500 * (self.wave_count - 1)} WAVE BONUS!", True, (90, 230, 255))
        surface.blit(bonus, (WIDTH // 2 - bonus.get_width() // 2, 215))

        next_txt = self.health_font.render(f"PREPARING WAVE {self.wave_count}...", True, WHITE)
        surface.blit(next_txt, (WIDTH // 2 - next_txt.get_width() // 2, 280))

    def render(self, now: int):
        # Calculate Screen Shake Offset
        offset_x, offset_y = 0, 0
        if now < self.shake_until:
            offset_x = random.randint(-self.shake_amount, self.shake_amount)
            offset_y = random.randint(-self.shake_amount, self.shake_amount)

        render_surface = pygame.Surface((WIDTH, HEIGHT))

        if self.state == "menu":
            self.draw_menu(render_surface)
        elif self.state == "game_over":
            self.draw_winner(render_surface)
        elif self.state == "level_clear":
            self.draw_level_clear(render_surface)
        elif self.state == "playing":
            render_surface.fill(BLACK)
            render_surface.blit(self.bg_space, (0, 0))
            self.starfield.draw(render_surface)
            
            # Battlefield Outer & Center Visual Boundaries
            pygame.draw.rect(render_surface, (60, 140, 240), (2, 60, WIDTH - 4, HEIGHT - 65), 2)
            pygame.draw.rect(render_surface, (80, 80, 130), BORDER)

            self.draw_hud(render_surface, now)

            # Draw Thruster Flame Particles
            for tp in self.thruster_particles:
                tp.draw(render_surface)

            # Draw PowerUps
            for pickup in self.powerups:
                pickup.draw(render_surface, self.powerup_font, now)

            # Draw Ships
            is_yellow_hit = (now < self.hit_feedback_until) and (self.hit_player == "yellow")
            is_red_hit = (now < self.hit_feedback_until) and (self.hit_player == "red")
            self.yellow.draw(render_surface, self.health_font, now, is_yellow_hit)
            self.red.draw(render_surface, self.health_font, now, is_red_hit)

            # Draw Bullets
            for bullet in self.yellow_bullets + self.red_bullets:
                bullet.draw(render_surface)

            # Draw VFX
            for flash in self.flashes:
                flash.draw(render_surface, now)
            for explosion in self.explosions:
                explosion.draw(render_surface, now)

            # Draw Floating Texts
            for ft in self.floating_texts:
                ft.draw(render_surface, self.powerup_font, now)

            if self.is_paused:
                self.draw_pause_navigation_menu(render_surface)

        self.window.fill(BLACK)
        self.window.blit(render_surface, (offset_x, offset_y))
        pygame.display.update()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            self.handle_events(now)

            # Floating text animations across all states
            for ft in self.floating_texts[:]:
                ft.update()
                if not ft.is_alive(now):
                    self.floating_texts.remove(ft)

            if self.state in ("playing", "level_clear"):
                self.update_physics_and_ai(now)

            self.render(now)

        self.save_high_score()
        pygame.quit()


def main():
    game = GalaxyShootersGame()
    game.run()


if __name__ == "__main__":
    main()
