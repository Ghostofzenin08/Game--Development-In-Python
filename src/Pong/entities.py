"""Game entities with no application-loop or rendering dependencies."""

import random
from collections import deque
from dataclasses import dataclass
from config import WIDTH, HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS


class Paddle:
    SPEED = 4
    def __init__(self, x, y):
        self.x, self.y, self.width, self.height = x, y, PADDLE_WIDTH, PADDLE_HEIGHT
        self.last_move = self.grow_until = 0

    @property
    def center_y(self): return self.y + self.height / 2

    def update(self, now):
        self.height = PADDLE_HEIGHT * 1.5 if now < self.grow_until else PADDLE_HEIGHT
        self.y = max(0, min(self.y, HEIGHT - self.height))

    def move(self, direction):
        self.last_move = direction
        self.y = max(0, min(self.y + direction * self.SPEED, HEIGHT - self.height))

    def stop(self): self.last_move = 0


class Ball:
    BASE_SPEED, SPEED_INCREASE, MAX_SPEED = 5, .45, 10
    def __init__(self):
        self.radius, self.trail = BALL_RADIUS, deque(maxlen=10)
        self.reset()

    def reset(self):
        self.x, self.y, self.speed = WIDTH / 2, HEIGHT / 2, self.BASE_SPEED
        self.x_vel = random.choice((-1, 1)) * self.speed
        self.y_vel = random.choice((-1, 1)) * random.uniform(1.2, 2.8)
        self.trail.clear()

    def move(self):
        self.trail.append((self.x, self.y)); self.x += self.x_vel; self.y += self.y_vel

    def speed_up(self): self.speed = min(self.speed + self.SPEED_INCREASE, self.MAX_SPEED)
    def slow_down(self):
        self.speed = max(self.BASE_SPEED, self.speed - 2)
        self.x_vel = (-1 if self.x_vel < 0 else 1) * self.speed
        self.y_vel *= .7


@dataclass
class PowerUp:
    kind: str; x: int; y: int; expires_at: int
    @classmethod
    def spawn(cls, now):
        return cls(random.choice(("grow", "slow")), random.randint(230, 470), random.randint(100, 400), now + 6500)


@dataclass
class Flash:
    x: float; y: float; color: tuple; size: int = 20; life: int = 12
    def tick(self):
        self.life -= 1; self.size += 2
        return self.life > 0
