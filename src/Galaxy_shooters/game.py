import pygame
import os
import random


pygame.init()
pygame.font.init()


ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'images')
SOUND_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')


WIDTH, HEIGHT = 900, 500

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shooters")

WHITE = (255, 255, 255)

HEALTH_FONT = pygame.font.SysFont('comicsans', 30)
HEALTH_SMALL_FONT = pygame.font.SysFont('comicsans', 20)
TITLE_FONT = pygame.font.SysFont('comicsans', 52)
MENU_FONT = pygame.font.SysFont('comicsans', 32)
POWERUP_FONT = pygame.font.SysFont('arial', 17, bold=True)

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)

BLACK = (0, 0, 0 )
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


FPS = 60
VEL = 5

BULLET_VEL = 7
MAX_BULLETS = 3
MAX_HEALTH = 10
HEALTH_BAR_WIDTH = 220
HEALTH_BAR_HEIGHT = 18
POWERUP_SIZE = 28
POWERUP_SPAWN_MS = 7000
POWERUP_DURATION_MS = 6500

POWERUPS = {
    "rapid": {"label": "RAPID", "icon": "⚡", "color": (90, 220, 255)},
    "shield": {"label": "SHIELD", "icon": "S", "color": (100, 160, 255)},
    "health": {"label": "+HEALTH", "icon": "+", "color": (90, 230, 120)},
    "double": {"label": "DOUBLE", "icon": "2X", "color": (255, 145, 235)},
    "speed": {"label": "SPEED", "icon": "»", "color": (255, 180, 55)},
}


SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT+ 2



YELLOW_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join(ASSET_DIR, 'yellow_spaceship.png'))
YELLOW_SPACESHIP_IMAGE = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join(ASSET_DIR, 'red_spaceship.png'))
RED_SPACESHIP_IMAGE = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

SPACE = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, 'background_GS.png')), (WIDTH, HEIGHT))

LASER_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'laser_GS.mp3'))
HIT_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'damage_GS.mp3'))
VICTORY_SOUND = pygame.mixer.Sound(os.path.join(SOUND_DIR, 'victory_GS.mp3'))
BACKGROUND_MUSIC = os.path.join(SOUND_DIR, 'background_GS.mp3')


def make_laser_sprite(color, direction):
    """Create a small glowing laser sprite without needing an image asset."""
    sprite = pygame.Surface((36, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(sprite, (*color, 45), (1, 2, 34, 12))
    pygame.draw.ellipse(sprite, (*color, 115), (5, 4, 27, 8))
    pygame.draw.rect(sprite, (*color, 225), (7, 5, 22, 6), border_radius=3)
    pygame.draw.ellipse(sprite, (255, 255, 255, 255), (10, 6, 17, 4))
    return sprite if direction == 1 else pygame.transform.flip(sprite, True, False)


YELLOW_LASER = make_laser_sprite(YELLOW, 1)
RED_LASER = make_laser_sprite(RED, -1)


def spawn_muzzle_flash(flashes, ship, color, direction):
    flashes.append({
        "center": (ship.right if direction == 1 else ship.left, ship.centery),
        "color": color,
        "created": pygame.time.get_ticks(),
        "direction": direction,
    })


def spawn_explosion(explosions, center, color):
    explosions.append({"center": center, "color": color,
                       "created": pygame.time.get_ticks()})


def spawn_powerup(powerups):
    """Place a pickup on either player's side, away from the centre barrier."""
    kind = random.choice(list(POWERUPS))
    side_x = random.choice((random.randint(55, BORDER.left - 55),
                            random.randint(BORDER.right + 25, WIDTH - 55)))
    powerups.append({"kind": kind,
                     "rect": pygame.Rect(side_x, random.randint(85, HEIGHT - 65),
                                         POWERUP_SIZE, POWERUP_SIZE),
                     "created": pygame.time.get_ticks()})


def activate_powerup(kind, player, health, effects):
    now = pygame.time.get_ticks()
    if kind == "health":
        health = min(MAX_HEALTH, health + 3)
    else:
        effects[player][kind] = now + POWERUP_DURATION_MS
    return health


def effect_active(effects, player, kind):
    return effects[player].get(kind, 0) > pygame.time.get_ticks()


def draw_powerups(powerups, effects):
    now = pygame.time.get_ticks()
    for pickup in powerups[:]:
        if now - pickup["created"] > 10000:
            powerups.remove(pickup)
            continue
        info = POWERUPS[pickup["kind"]]
        rect = pickup["rect"]
        pulse = int(3 * abs((now % 500) / 250 - 1))
        pygame.draw.circle(WIN, (*info["color"], 80), rect.center, rect.width // 2 + 5 + pulse)
        pygame.draw.circle(WIN, info["color"], rect.center, rect.width // 2)
        pygame.draw.circle(WIN, WHITE, rect.center, rect.width // 2, 2)
        icon = POWERUP_FONT.render(info["icon"], True, BLACK)
        WIN.blit(icon, icon.get_rect(center=rect.center))

    for player, x, align_right in (("yellow", 10, False), ("red", WIDTH - 10, True)):
        active = [POWERUPS[kind]["label"] for kind in ("rapid", "shield", "double", "speed")
                  if effect_active(effects, player, kind)]
        if active:
            text = POWERUP_FONT.render(" | ".join(active), True, WHITE)
            text_x = x - text.get_width() if align_right else x
            WIN.blit(text, (text_x, 54))


def draw_health_bar(x, y, health, color, align_right=False):
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
    pygame.draw.rect(WIN, BLACK, background)
    pygame.draw.rect(WIN, state_color, fill)
    pygame.draw.rect(WIN, WHITE, background, 2)

    health_text = HEALTH_SMALL_FONT.render(
        f"{max(0, health)}/{MAX_HEALTH}", True, WHITE)
    text_x = bar_x + HEALTH_BAR_WIDTH - health_text.get_width() - 5
    WIN.blit(health_text, (text_x, y - health_text.get_height() - 2))


def draw_effects(bullets, flashes, explosions):
    now = pygame.time.get_ticks()

    # A fading beam tail and halo make each laser readable against the starfield.
    for bullet in bullets:
        rect = bullet["rect"]
        direction = bullet["direction"]
        color = bullet["color"]
        tail_length = 26
        tail = pygame.Rect(rect.centerx - (tail_length if direction == 1 else 0),
                           rect.centery - 2, tail_length, 4)
        pygame.draw.rect(WIN, (*color, 55), tail, border_radius=2)
        glow = pygame.Surface((46, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*color, 45), (0, 3, 46, 18))
        WIN.blit(glow, (rect.centerx - 23, rect.centery - 12))
        sprite = YELLOW_LASER if color == YELLOW else RED_LASER
        WIN.blit(sprite, sprite.get_rect(center=rect.center))

    for flash in flashes[:]:
        age = now - flash["created"]
        if age >= 100:
            flashes.remove(flash)
            continue
        progress = age / 100
        radius = int(15 * (1 - progress)) + 3
        alpha = int(230 * (1 - progress))
        layer = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = (radius * 2, radius * 2)
        pygame.draw.circle(layer, (*flash["color"], alpha // 3), center, radius * 2)
        pygame.draw.circle(layer, (255, 255, 255, alpha), center, radius)
        WIN.blit(layer, layer.get_rect(center=flash["center"]))

    # Expanding rings provide a clear hit animation and a brief explosion burst.
    for explosion in explosions[:]:
        age = now - explosion["created"]
        if age >= 360:
            explosions.remove(explosion)
            continue
        progress = age / 360
        radius = max(2, int(8 + progress * 32))
        alpha = int(255 * (1 - progress))
        layer = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        center = (radius * 2, radius * 2)
        pygame.draw.circle(layer, (*explosion["color"], alpha // 3), center, radius + 10)
        pygame.draw.circle(layer, (255, 245, 180, alpha), center, radius, 2)
        for angle in range(0, 360, 60):
            offset_x = int(radius * 1.25 * pygame.math.Vector2(1, 0).rotate(angle).x)
            offset_y = int(radius * 1.25 * pygame.math.Vector2(1, 0).rotate(angle).y)
            pygame.draw.circle(layer, (*explosion["color"], alpha),
                               (center[0] + offset_x, center[1] + offset_y), 3)
        WIN.blit(layer, layer.get_rect(center=explosion["center"]))


def draw_window(yellow, red, red_bullets, yellow_bullets, red_health,
                yellow_health, hit_player, hit_feedback_until, flashes,
                explosions, powerups, effects):
    WIN.fill(WHITE)
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)
    draw_health_bar(10, 28, yellow_health, YELLOW)
    draw_health_bar(WIDTH - 10, 28, red_health, RED, align_right=True)
    draw_powerups(powerups, effects)

    WIN.blit(YELLOW_SPACESHIP_IMAGE, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP_IMAGE, (red.x, red.y))

    # A shield is always visible, so players can tell why a hit did no damage.
    for ship, player, color in ((yellow, "yellow", YELLOW), (red, "red", RED)):
        if effect_active(effects, player, "shield"):
            pygame.draw.ellipse(WIN, (110, 185, 255), ship.inflate(18, 18), 2)

    if pygame.time.get_ticks() < hit_feedback_until:
        hit_ship = red if hit_player == "red" else yellow
        pygame.draw.rect(WIN, WHITE, hit_ship.inflate(12, 12), 3)
        hit_text = HEALTH_FONT.render("HIT!", True, WHITE)
        WIN.blit(hit_text, (hit_ship.centerx - hit_text.get_width() // 2,
                            hit_ship.y - hit_text.get_height() - 8))

    draw_effects(yellow_bullets + red_bullets, flashes, explosions)

    pygame.display.update()


def yellow_handle_movement(keys_pressed, yellow, speed):
    if keys_pressed[pygame.K_a] and yellow.x - speed > 0: # LEFT
        yellow.x -= speed
    if keys_pressed[pygame.K_d] and yellow.x + speed + yellow.width < BORDER.x: # RIGHT
        yellow.x += speed
    if keys_pressed[pygame.K_w] and yellow.y - speed > 0: # UP
        yellow.y -= speed
    if keys_pressed[pygame.K_s] and yellow.y + speed + yellow.height < HEIGHT - 15: # DOWN
        yellow.y += speed


def red_handle_movement(keys_pressed, red, speed):
    if keys_pressed[pygame.K_LEFT] and red.x - speed > BORDER.x + BORDER.width : # LEFT
        red.x -= speed
    if keys_pressed[pygame.K_RIGHT] and red.x + speed + red.width < WIDTH: # RIGHT
        red.x += speed
    if keys_pressed[pygame.K_UP] and red.y - speed > 0: # UP
        red.y -= speed
    if keys_pressed[pygame.K_DOWN] and red.y + speed + red.height < HEIGHT - 15: # DOWN
        red.y += speed


def fire_laser(player, ship, bullets, flashes, effects, last_shot):
    """Fire one laser, or a spaced pair while Double Shot is active."""
    now = pygame.time.get_ticks()
    rapid = effect_active(effects, player, "rapid")
    cooldown = 110 if rapid else 250
    bullet_limit = 6 if rapid else MAX_BULLETS
    if now - last_shot[player] < cooldown or len(bullets) >= bullet_limit:
        return

    direction = 1 if player == "yellow" else -1
    color = YELLOW if player == "yellow" else RED
    offsets = (-9, 9) if effect_active(effects, player, "double") else (0,)
    for offset in offsets:
        if len(bullets) >= bullet_limit:
            break
        x = ship.right - 2 if direction == 1 else ship.left - 14
        bullets.append({"rect": pygame.Rect(x, ship.centery - 3 + offset, 16, 6),
                        "color": color, "direction": direction})
    spawn_muzzle_flash(flashes, ship, color, direction)
    LASER_SOUND.play()
    last_shot[player] = now


def handle_bullets(yellow_bullets, red_bullets, yellow, red, explosions):
    for bullet in yellow_bullets[:]:
        bullet["rect"].x += BULLET_VEL
        if red.colliderect(bullet["rect"]):
            pygame.event.post(pygame.event.Event(RED_HIT))
            spawn_explosion(explosions, bullet["rect"].center, YELLOW)
            yellow_bullets.remove(bullet)
        elif bullet["rect"].x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet["rect"].x -= BULLET_VEL
        if yellow.colliderect(bullet["rect"]):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            spawn_explosion(explosions, bullet["rect"].center, RED)
            red_bullets.remove(bullet)
        elif bullet["rect"].x < 0:
            red_bullets.remove(bullet)


def draw_menu():
    WIN.blit(SPACE, (0, 0))
    title_text = TITLE_FONT.render("GALAXY SHOOTERS", True, WHITE)
    subtitle_text = MENU_FONT.render("2 PLAYER SPACE BATTLE", True, WHITE)
    start_text = MENU_FONT.render("[ START GAME ]", True, WHITE)
    controls_text = MENU_FONT.render("[ CONTROLS ]", True, WHITE)
    quit_text = MENU_FONT.render("[ QUIT ]", True, WHITE)

    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 70))
    WIN.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, 145))
    WIN.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 245))
    WIN.blit(controls_text, (WIDTH // 2 - controls_text.get_width() // 2, 300))
    WIN.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 355))
    pygame.display.update()


def draw_winner(text):
    WIN.blit(SPACE, (0, 0))
    winner_text = TITLE_FONT.render(text, True, WHITE)
    WIN.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2,
                           HEIGHT // 2 - winner_text.get_height() // 2))
    restart_text = MENU_FONT.render("Press R to Restart", True, WHITE)
    quit_text = MENU_FONT.render("Press ESC to Quit", True, WHITE)
    WIN.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 315))
    WIN.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, 355))
    pygame.display.update()


def new_game():
    return (
        pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT),
        pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT),
        [],
        [],
        MAX_HEALTH,
        MAX_HEALTH,
        [],
        [],
        [],
        {"yellow": {}, "red": {}},
    )


def main():
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.set_volume(0.35)
    VICTORY_SOUND.set_volume(1.0)
    pygame.mixer.music.play(-1)
    victory_channel = pygame.mixer.Channel(0)
    clock = pygame.time.Clock()
    run = True
    game_started = False
    winner_text = ""
    hit_player = None
    hit_feedback_until = 0
    yellow, red, yellow_bullets, red_bullets, red_health, yellow_health, flashes, explosions, powerups, effects = new_game()
    last_shot = {"yellow": -1000, "red": -1000}
    next_powerup_spawn = pygame.time.get_ticks() + POWERUP_SPAWN_MS

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


            if event.type == pygame.KEYDOWN and winner_text:
                if event.key == pygame.K_r:
                    yellow, red, yellow_bullets, red_bullets, red_health, yellow_health, flashes, explosions, powerups, effects = new_game()
                    last_shot = {"yellow": -1000, "red": -1000}
                    next_powerup_spawn = pygame.time.get_ticks() + POWERUP_SPAWN_MS
                    winner_text = ""
                    hit_player = None
                    hit_feedback_until = 0
                    pygame.mixer.music.play(-1)
                elif event.key == pygame.K_ESCAPE:
                    run = False

            if event.type == pygame.KEYDOWN and not game_started and not winner_text:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_started = True
                elif event.key == pygame.K_ESCAPE:
                    run = False

            if event.type == pygame.KEYDOWN and game_started and not winner_text:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    fire_laser("yellow", yellow, yellow_bullets, flashes, effects, last_shot)

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    fire_laser("red", red, red_bullets, flashes, effects, last_shot)

            if event.type == RED_HIT and game_started and not winner_text:
                if not effect_active(effects, "red", "shield"):
                    red_health -= 1
                hit_player = "red"
                hit_feedback_until = pygame.time.get_ticks() + 250
                HIT_SOUND.play()

            if event.type == YELLOW_HIT and game_started and not winner_text:
                if not effect_active(effects, "yellow", "shield"):
                    yellow_health -= 1
                hit_player = "yellow"
                hit_feedback_until = pygame.time.get_ticks() + 250
                HIT_SOUND.play()

        if not game_started:
            draw_winner(winner_text) if winner_text else draw_menu()
            continue

        if not winner_text and red_health <= 0:
            winner_text = "Yellow wins!"
            pygame.mixer.music.fadeout(250)
            victory_channel.play(VICTORY_SOUND)
        elif not winner_text and yellow_health <= 0:
            winner_text = "Red wins!"
            pygame.mixer.music.fadeout(250)
            victory_channel.play(VICTORY_SOUND)

        if winner_text:
            draw_winner(winner_text)
            continue

        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow,
                               VEL + 3 if effect_active(effects, "yellow", "speed") else VEL)
        red_handle_movement(keys_pressed, red,
                            VEL + 3 if effect_active(effects, "red", "speed") else VEL)

        # Rapid Fire works while the player holds their existing fire key.
        if effect_active(effects, "yellow", "rapid") and keys_pressed[pygame.K_LCTRL]:
            fire_laser("yellow", yellow, yellow_bullets, flashes, effects, last_shot)
        if effect_active(effects, "red", "rapid") and keys_pressed[pygame.K_RCTRL]:
            fire_laser("red", red, red_bullets, flashes, effects, last_shot)

        if pygame.time.get_ticks() >= next_powerup_spawn:
            spawn_powerup(powerups)
            next_powerup_spawn = pygame.time.get_ticks() + POWERUP_SPAWN_MS

        for pickup in powerups[:]:
            if yellow.colliderect(pickup["rect"]):
                yellow_health = activate_powerup(pickup["kind"], "yellow", yellow_health, effects)
                powerups.remove(pickup)
            elif red.colliderect(pickup["rect"]):
                red_health = activate_powerup(pickup["kind"], "red", red_health, effects)
                powerups.remove(pickup)

        handle_bullets(yellow_bullets, red_bullets, yellow, red, explosions)

        draw_window(
            yellow,
            red,
            red_bullets,
            yellow_bullets,
            red_health,
            yellow_health,
            hit_player,
            hit_feedback_until,
            flashes,
            explosions,
            powerups,
            effects
        )



    pygame.quit()



if __name__ == "__main__":
    main()
