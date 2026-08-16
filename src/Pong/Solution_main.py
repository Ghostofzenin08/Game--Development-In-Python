import random
import pygame

WIDTH, HEIGHT, FPS = 700, 500, 60
WINNING_SCORE, COUNTDOWN_SECONDS = 5, 3
PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS = 20, 100, 7
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (170, 170, 170)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
SCORE_FONT = pygame.font.SysFont("comicsans", 50)
TITLE_FONT = pygame.font.SysFont("comicsans", 72, bold=True)
MENU_FONT = pygame.font.SysFont("comicsans", 30)


class Paddle:
    VEL = 4

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = PADDLE_WIDTH, PADDLE_HEIGHT

    def draw(self):
        pygame.draw.rect(WIN, WHITE, (self.x, self.y, self.width, self.height))

    def move(self, up):
        self.y += -self.VEL if up else self.VEL


class Ball:
    BASE_SPEED, SPEED_INCREASE, MAX_SPEED = 5, 0.45, 10

    def __init__(self):
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        self.radius = BALL_RADIUS
        self.x_vel = self.y_vel = 0
        self.speed = self.BASE_SPEED

    def draw(self):
        pygame.draw.circle(WIN, WHITE, (round(self.x), round(self.y)), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        """Start each serve in a random horizontal direction with a small vertical angle."""
        self.x, self.y, self.speed = WIDTH / 2, HEIGHT / 2, self.BASE_SPEED
        self.x_vel = random.choice((-1, 1)) * self.speed
        self.y_vel = random.choice((-1, 1)) * random.uniform(1.2, 2.8)

    def speed_up(self):
        self.speed = min(self.speed + self.SPEED_INCREASE, self.MAX_SPEED)


def centered(text, y, font=MENU_FONT, color=WHITE):
    surface = font.render(text, True, color)
    WIN.blit(surface, (WIDTH // 2 - surface.get_width() // 2, y))


def draw_game(paddles, ball, left_score, right_score, countdown=None):
    WIN.fill(BLACK)
    for x, score in ((WIDTH // 4, left_score), (WIDTH * 3 // 4, right_score)):
        surface = SCORE_FONT.render(str(score), True, WHITE)
        WIN.blit(surface, (x - surface.get_width() // 2, 20))
    for y in range(10, HEIGHT, HEIGHT // 10):
        pygame.draw.rect(WIN, WHITE, (WIDTH // 2 - 5, y, 10, HEIGHT // 20))
    for paddle in paddles:
        paddle.draw()
    ball.draw()
    if countdown is not None:
        centered(f"Serve in {countdown}", HEIGHT // 2 - 100)
    pygame.display.flip()


def draw_start_screen():
    WIN.fill(BLACK)
    centered("PONG", 115, TITLE_FONT)
    centered("Press SPACE or ENTER to start", 245)
    centered(f"First to {WINNING_SCORE} wins  |  W/S and Arrow Keys", 300, MENU_FONT, GRAY)
    pygame.display.flip()


def draw_winner(left_score, right_score):
    WIN.fill(BLACK)
    winner = "Left player" if left_score > right_score else "Right player"
    centered(f"{winner} wins!", 165, TITLE_FONT)
    centered("Press R to play again or ESC to quit", 270)
    pygame.display.flip()


def handle_collision(ball, left, right):
    if ball.y + ball.radius >= HEIGHT or ball.y - ball.radius <= 0:
        ball.y = min(max(ball.y, ball.radius), HEIGHT - ball.radius)
        ball.y_vel *= -1

    paddle = left if ball.x_vel < 0 else right
    reaches_paddle = ball.x - ball.radius <= paddle.x + paddle.width if ball.x_vel < 0 else ball.x + ball.radius >= paddle.x
    if paddle.y <= ball.y <= paddle.y + paddle.height and reaches_paddle:
        ball.x = paddle.x + paddle.width + ball.radius if ball.x_vel < 0 else paddle.x - ball.radius
        # Paddle position gives the ball its vertical angle; every return increases speed.
        ball.y_vel = ((ball.y - (paddle.y + paddle.height / 2)) / (paddle.height / 2)) * ball.speed
        ball.speed_up()
        ball.x_vel = ball.speed if ball.x_vel < 0 else -ball.speed


def move_paddles(keys, left, right):
    if keys[pygame.K_w] and left.y > 0:
        left.move(True)
    if keys[pygame.K_s] and left.y + left.height < HEIGHT:
        left.move(False)
    if keys[pygame.K_UP] and right.y > 0:
        right.move(True)
    if keys[pygame.K_DOWN] and right.y + right.height < HEIGHT:
        right.move(False)


def main():
    clock = pygame.time.Clock()
    left, right = Paddle(10, 200), Paddle(WIDTH - 10 - PADDLE_WIDTH, 200)
    ball = Ball()
    state, left_score, right_score, countdown_start = "start", 0, 0, 0
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if state == "start" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    left_score = right_score = 0
                    ball.reset()
                    countdown_start, state = pygame.time.get_ticks(), "countdown"
                elif state == "game_over" and event.key == pygame.K_r:
                    state = "start"
                elif state == "game_over" and event.key == pygame.K_ESCAPE:
                    running = False

        if state == "start":
            draw_start_screen()
        elif state == "game_over":
            draw_winner(left_score, right_score)
        elif state == "countdown":
            elapsed = pygame.time.get_ticks() - countdown_start
            draw_game([left, right], ball, left_score, right_score, max(1, COUNTDOWN_SECONDS - elapsed // 1000))
            if elapsed >= COUNTDOWN_SECONDS * 1000:
                state = "playing"
        else:
            move_paddles(pygame.key.get_pressed(), left, right)
            ball.move()
            handle_collision(ball, left, right)
            if ball.x < 0 or ball.x > WIDTH:
                if ball.x < 0:
                    right_score += 1
                else:
                    left_score += 1
                if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
                    state = "game_over"
                else:
                    ball.reset()
                    countdown_start, state = pygame.time.get_ticks(), "countdown"
            draw_game([left, right], ball, left_score, right_score)
    pygame.quit()


if __name__ == "__main__":
    main()
