"""Galaxy Shooters: Space Battle Arcade Game (Refactored with OOP Classes)."""

import os
import random
import pygame


# =====================================================================
# Configuration & Constants
# =====================================================================
WIDTH, HEIGHT = 900, 500
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
MAX_HEALTH = 10
HEALTH_BAR_WIDTH = 220
HEALTH_BAR_HEIGHT = 18

POWERUP_SIZE = 28
POWERUP_SPAWN_MS = 7000
POWERUP_DURATION_MS = 6500
AI_VEL = 4
AI_FIRE_INTERVAL_MS = 420

BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)

POWERUP_CONFIG = {
    "rapid": {"label": "RAPID", "icon": "⚡", "color": (90, 220, 255)},
    "shield": {"label": "SHIELD", "icon": "S", "color": (100, 160, 255)},
    "health": {"label": "+HEALTH", "icon": "+", "color": (90, 230, 120)},
    "double": {"label": "DOUBLE", "icon": "2X", "color": (255, 145, 235)},
    "speed": {"label": "SPEED", "icon": "»", "color": (255, 180, 55)},
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
        progress = age / self.duration_ms
        radius = int(15 * (1 - progress)) + 3
        alpha = int(230 * (1 - progress))
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
        progress = age / self.duration_ms
        radius = max(2, int(8 + progress * 32))
        alpha = int(255 * (1 - progress))
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
            if self.rect.y - speed > 0:
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
    ):
        """Pursues opponent, dodges incoming fire, and collects available powerups."""
        target_y = target_ship.rect.centery

        # Dodge the nearest dangerous laser heading toward the ship
        threats = [b for b in incoming_bullets if b.rect.x < self.rect.left]
        if threats:
            threat = max(threats, key=lambda b: b.rect.x)
            if abs(threat.rect.centery - self.rect.centery) < 75:
                target_y = 70 if threat.rect.centery > self.rect.centery else screen_height - 70
        else:
            ai_pickups = [p for p in powerups if p.rect.centerx > border_rect.right]
            if ai_pickups:
                target_y = min(
                    ai_pickups,
                    key=lambda p: abs(p.rect.centery - self.rect.centery),
                ).rect.centery

        speed = self.get_speed(now)
        if self.rect.centery < target_y - 10 and self.rect.bottom + speed < screen_height - 15:
            self.rect.y += speed
        elif self.rect.centery > target_y + 10 and self.rect.top - speed > 0:
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
        self.laser_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "laser_GS.mp3"))
        self.hit_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "damage_GS.mp3"))
        self.victory_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "victory_GS.mp3"))
        self.victory_sound.set_volume(1.0)
        self.victory_channel = pygame.mixer.Channel(0)
        self.bg_music_path = os.path.join(SOUND_DIR, "background_GS.mp3")

    def play_music(self):
        pygame.mixer.music.load(self.bg_music_path)
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)

    def fadeout_music(self, ms: int = 250):
        pygame.mixer.music.fadeout(ms)

    def play_laser(self):
        self.laser_sound.play()

    def play_hit(self):
        self.hit_sound.play()

    def play_victory(self):
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
        self.bg_space = pygame.transform.scale(
            pygame.image.load(os.path.join(ASSET_DIR, "background_GS.png")),
            (WIDTH, HEIGHT),
        )

        yellow_raw = pygame.image.load(os.path.join(ASSET_DIR, "yellow_spaceship.png"))
        self.yellow_img = pygame.transform.rotate(
            pygame.transform.scale(yellow_raw, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)),
            90,
        )

        red_raw = pygame.image.load(os.path.join(ASSET_DIR, "red_spaceship.png"))
        self.red_img = pygame.transform.rotate(
            pygame.transform.scale(red_raw, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)),
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
                "fire": pygame.K_LCTRL,
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

        # Game State
        self.running = True
        self.game_mode = "ai"  # 'ai' or 'two'
        self.state = "menu"  # 'menu', 'playing', 'game_over'
        self.winner_text = ""
        self.hit_player = None
        self.hit_feedback_until = 0
        self.next_powerup_spawn = 0

    def reset_match(self):
        now = pygame.time.get_ticks()
        self.yellow.reset(100, 300)
        self.red.reset(700, 300)
        self.red.is_ai = self.game_mode == "ai"
        self.yellow_bullets.clear()
        self.red_bullets.clear()
        self.flashes.clear()
        self.explosions.clear()
        self.powerups.clear()
        self.hit_player = None
        self.hit_feedback_until = 0
        self.winner_text = ""
        self.next_powerup_spawn = now + POWERUP_SPAWN_MS
        self.audio.play_music()
        self.state = "playing"

    def handle_events(self, now: int):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_1:
                        self.game_mode = "ai"
                    elif event.key == pygame.K_2:
                        self.game_mode = "two"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_match()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state == "playing":
                    # Yellow Fire Trigger
                    if event.key == self.yellow.controls.get("fire"):
                        bullets, flash = self.yellow.fire(len(self.yellow_bullets), now)
                        if bullets:
                            self.yellow_bullets.extend(bullets)
                            self.flashes.append(flash)
                            self.audio.play_laser()

                    # Red Fire Trigger (Human mode)
                    if (
                        self.game_mode == "two"
                        and event.key == self.red.controls.get("fire")
                    ):
                        bullets, flash = self.red.fire(len(self.red_bullets), now)
                        if bullets:
                            self.red_bullets.extend(bullets)
                            self.flashes.append(flash)
                            self.audio.play_laser()

                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                        self.audio.fadeout_music()

                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.reset_match()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"

    def update_physics_and_ai(self, now: int):
        keys = pygame.key.get_pressed()

        # Ship Movement
        self.yellow.move_human(keys, now, HEIGHT)

        if self.game_mode == "ai":
            self.red.update_ai(
                self.yellow,
                self.yellow_bullets,
                self.powerups,
                now,
                BORDER,
                HEIGHT,
            )
            # AI automatic firing logic
            if now >= self.red.next_ai_shot_time:
                bullets, flash = self.red.fire(len(self.red_bullets), now)
                if bullets:
                    self.red_bullets.extend(bullets)
                    self.flashes.append(flash)
                    self.audio.play_laser()
                self.red.next_ai_shot_time = now + AI_FIRE_INTERVAL_MS
        else:
            self.red.move_human(keys, now, HEIGHT)

        # Rapid Fire continuous stream while holding fire key
        if self.yellow.is_effect_active("rapid", now) and keys[self.yellow.controls["fire"]]:
            bullets, flash = self.yellow.fire(len(self.yellow_bullets), now)
            if bullets:
                self.yellow_bullets.extend(bullets)
                self.flashes.append(flash)
                self.audio.play_laser()

        if (
            self.game_mode == "two"
            and self.red.is_effect_active("rapid", now)
            and keys[self.red.controls["fire"]]
        ):
            bullets, flash = self.red.fire(len(self.red_bullets), now)
            if bullets:
                self.red_bullets.extend(bullets)
                self.flashes.append(flash)
                self.audio.play_laser()

        # PowerUp Spawning & Lifecycles
        if now >= self.next_powerup_spawn:
            self.powerups.append(PowerUp.spawn(BORDER, WIDTH, HEIGHT, now))
            self.next_powerup_spawn = now + POWERUP_SPAWN_MS

        for pickup in self.powerups[:]:
            if pickup.is_expired(now):
                self.powerups.remove(pickup)
            elif self.yellow.rect.colliderect(pickup.rect):
                self.yellow.apply_powerup(pickup.kind, now)
                self.powerups.remove(pickup)
            elif self.red.rect.colliderect(pickup.rect):
                self.red.apply_powerup(pickup.kind, now)
                self.powerups.remove(pickup)

        # Bullets movement & collisions
        for bullet in self.yellow_bullets[:]:
            bullet.update()
            if self.red.rect.colliderect(bullet.rect):
                self.yellow_bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.rect.center, YELLOW))
                self.red.take_damage(now)
                self.hit_player = "red"
                self.hit_feedback_until = now + 250
                self.audio.play_hit()
            elif bullet.is_offscreen(WIDTH):
                self.yellow_bullets.remove(bullet)

        for bullet in self.red_bullets[:]:
            bullet.update()
            if self.yellow.rect.colliderect(bullet.rect):
                self.red_bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.rect.center, RED))
                self.yellow.take_damage(now)
                self.hit_player = "yellow"
                self.hit_feedback_until = now + 250
                self.audio.play_hit()
            elif bullet.is_offscreen(WIDTH):
                self.red_bullets.remove(bullet)

        # Clean up finished visual effects
        self.flashes = [f for f in self.flashes if f.is_alive(now)]
        self.explosions = [e for e in self.explosions if e.is_alive(now)]

        # Check win/loss conditions
        if self.red.health <= 0:
            self.winner_text = "You win!" if self.game_mode == "ai" else "Yellow wins!"
            self.state = "game_over"
            self.audio.fadeout_music(250)
            self.audio.play_victory()
        elif self.yellow.health <= 0:
            self.winner_text = "Computer wins!" if self.game_mode == "ai" else "Red wins!"
            self.state = "game_over"
            self.audio.fadeout_music(250)
            self.audio.play_victory()

    def draw_health_bar(self, x: int, y: int, health: int, color: tuple, align_right: bool = False):
        health_ratio = max(0, health) / MAX_HEALTH
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
        pygame.draw.rect(self.window, BLACK, background)
        pygame.draw.rect(self.window, state_color, fill)
        pygame.draw.rect(self.window, WHITE, background, 2)

        health_text = self.health_small_font.render(f"{max(0, health)}/{MAX_HEALTH}", True, WHITE)
        text_x = bar_x + HEALTH_BAR_WIDTH - health_text.get_width() - 5
        self.window.blit(health_text, (text_x, y - health_text.get_height() - 2))

    def draw_hud(self, now: int):
        # Health bars
        self.draw_health_bar(10, 28, self.yellow.health, YELLOW)
        self.draw_health_bar(WIDTH - 10, 28, self.red.health, RED, align_right=True)

        # Active powerup status texts
        yellow_active = self.yellow.get_active_labels(now)
        if yellow_active:
            text = self.powerup_font.render(" | ".join(yellow_active), True, WHITE)
            self.window.blit(text, (10, 54))

        red_active = self.red.get_active_labels(now)
        if red_active:
            text = self.powerup_font.render(" | ".join(red_active), True, WHITE)
            self.window.blit(text, (WIDTH - 10 - text.get_width(), 54))

    def draw_menu(self):
        self.window.blit(self.bg_space, (0, 0))
        title_text = self.title_font.render("GALAXY SHOOTERS", True, WHITE)
        subtitle_text = self.menu_font.render("SPACE BATTLE", True, WHITE)
        ai_text = self.menu_font.render(
            "1  PLAYER VS AI", True, YELLOW if self.game_mode == "ai" else WHITE
        )
        two_player_text = self.menu_font.render(
            "2  TWO PLAYERS", True, YELLOW if self.game_mode == "two" else WHITE
        )
        start_text = self.health_small_font.render("Press ENTER or SPACE to start", True, WHITE)
        controls_text = self.health_small_font.render(
            "Player: W A S D + Left Ctrl    Player 2: Arrow keys + Right Ctrl",
            True,
            WHITE,
        )
        quit_text = self.health_small_font.render("ESC to quit", True, WHITE)

        self.window.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 70))
        self.window.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 145))
        self.window.blit(ai_text, (WIDTH // 2 - ai_text.get_width() // 2, 225))
        self.window.blit(two_player_text, (WIDTH // 2 - two_player_text.get_width() // 2, 270))
        self.window.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 335))
        self.window.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 380))
        self.window.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 415))

    def draw_winner(self):
        self.window.blit(self.bg_space, (0, 0))
        winner_text = self.title_font.render(self.winner_text, True, WHITE)
        self.window.blit(
            winner_text,
            (
                WIDTH // 2 - winner_text.get_width() // 2,
                HEIGHT // 2 - winner_text.get_height() // 2,
            ),
        )
        restart_text = self.menu_font.render("Press R to Restart", True, WHITE)
        quit_text = self.menu_font.render("Press ESC for Menu", True, WHITE)
        self.window.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 315))
        self.window.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 355))

    def render(self, now: int):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game_over":
            self.draw_winner()
        elif self.state == "playing":
            self.window.fill(WHITE)
            self.window.blit(self.bg_space, (0, 0))
            pygame.draw.rect(self.window, BLACK, BORDER)

            self.draw_hud(now)

            # Draw PowerUps
            for pickup in self.powerups:
                pickup.draw(self.window, self.powerup_font, now)

            # Draw Ships
            is_yellow_hit = (now < self.hit_feedback_until) and (self.hit_player == "yellow")
            is_red_hit = (now < self.hit_feedback_until) and (self.hit_player == "red")
            self.yellow.draw(self.window, self.health_font, now, is_yellow_hit)
            self.red.draw(self.window, self.health_font, now, is_red_hit)

            # Draw Bullets
            for bullet in self.yellow_bullets + self.red_bullets:
                bullet.draw(self.window)

            # Draw VFX
            for flash in self.flashes:
                flash.draw(self.window, now)
            for explosion in self.explosions:
                explosion.draw(self.window, now)

        pygame.display.update()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            now = pygame.time.get_ticks()
            self.handle_events(now)

            if self.state == "playing":
                self.update_physics_and_ai(now)

            self.render(now)

        pygame.quit()


def main():
    game = GalaxyShootersGame()
    game.run()


if __name__ == "__main__":
    main()
