import pygame
import os
import random

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'images')



WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Galaxy Shooters")

WHITE = (255, 255, 255)

HEALTH_FONT = pygame.font.SysFont('comicsans', 30)

BORDER = pygame.Rect(WIDTH//2 - 5, 0, 10, HEIGHT)

BLACK = (0, 0, 0 )
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


FPS = 60
VEL = 5

BULLET_VEL = 7
MAX_BULLLETS = 3


SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT+ 2



YELLOW_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join(ASSET_DIR, 'yellow_spaceship.png'))
YELLOW_SPACESHIP_IMAGE = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)
RED_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join(ASSET_DIR, 'red_spaceship.png'))
RED_SPACESHIP_IMAGE = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

SPACE = pygame.transform.scale(pygame.image.load(os.path.join(ASSET_DIR, 'background_GS.png')), (WIDTH, HEIGHT))


def draw_window(yellow, red, red_bullets, yellow_bullets, red_health, yellow_health):
    WIN.fill(WHITE)
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)
    red_health_text = HEALTH_FONT.render(
        "Health:" + str(red_health), 1, WHITE)
    yellow_health_text = HEALTH_FONT.render(
        "Health:" + str(yellow_health),1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP_IMAGE, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP_IMAGE, (red.x, red.y))

    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)

    pygame.display.update()


def yellow_handle_movement(keys_pressed, yellow): 
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0: # LEFT
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x: # RIGHT
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0: # UP
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15: # DOWN
        yellow.y += VEL


def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width : # LEFT
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL+ red.width < WIDTH: # RIGHT
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0: # UP
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15: # DOWN
        red.y += VEL
  


def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets[:]:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets[:]:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x < 0:
            red_bullets.remove(bullet)


def draw_winner(text):
    winner_text = HEALTH_FONT.render(text, 1, WHITE)
    WIN.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2,
                           HEIGHT//2 - winner_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(3000)


def main():
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow_bullets = []
    red_bullets = []

    red_health = 10
    yellow_health = 10

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLLETS:
                    bullet = pygame.Rect(
                        yellow.x + yellow.width - 2, yellow.y + yellow.height//2 - 2, 10, 5)
                    yellow_bullets.append(bullet)

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLLETS:
                    bullet = pygame.Rect(
                        red.x + 2, red.y + red.height//2 - 2, 10, 5)
                    red_bullets.append(bullet)

            if event.type == RED_HIT:
                red_health -= 1

            if event.type == YELLOW_HIT:
                yellow_health -= 1

        winner_text = ""
        if red_health <= 0:
            winner_text = "Yellow wins!"
            

        if yellow_health <= 0:
            winner_text = "Red wins!"
            

        if winner_text != "":
            draw_winner(winner_text)
            break
            

        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red)

        handle_bullets(yellow_bullets, red_bullets, yellow, red)

        draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)



    pygame.quit()



if __name__ == "__main__":
    main()






