import pygame
import os

ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'images')



WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Galaxy Shooters")

WHITE = (255, 255, 255)

FPS = 60
VEL = 5


SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join(ASSET_DIR, 'yellow_spaceship.png'))
YELLOW_SPACESHIP_IMAGE = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join(ASSET_DIR, 'red_spaceship.png'))
RED_SPACESHIP_IMAGE = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)




def draw_window(red, yellow):
    WIN.fill(WHITE)
    WIN.blit(YELLOW_SPACESHIP_IMAGE, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP_IMAGE, (red.x, red.y))

    pygame.display.update()


def yellow_handle_movement(keys_pressed, yellow):
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_a]:  # LEFT 
        yellow.x -= VEL
    if keys_pressed[pygame.K_d]:  # RIGHT
        yellow.x += VEL
    if keys_pressed[pygame.K_w]:  # UP
        yellow.y -= VEL
    if keys_pressed[pygame.K_s]:  # DOWN
        yellow.y += VEL


def red_handle_movement(keys_pressed, red):
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_a]:  # LEFT 
        red.x -= VEL
    if keys_pressed[pygame.K_d]:  # RIGHT
        red.x += VEL
    if keys_pressed[pygame.K_w]:  # UP
        red.y -= VEL
    if keys_pressed[pygame.K_s]:  # DOWN
        red.y += VEL





def main():
    red = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)


    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False




        draw_window(red, yellow)



    pygame.quit()



if __name__ == "__main__":
    main()






