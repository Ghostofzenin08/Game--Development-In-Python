# Pong

A classic two-player Pong game built with **Python** and **Pygame**. The game recreates the original Pong experience with two paddles, a moving ball, collision detection, scoring, and keyboard controls for both players.

The project is designed as a simple introduction to game development with Pygame and demonstrates fundamental concepts such as game loops, keyboard input, object-oriented programming, collision detection, rendering, and score tracking.

## Features

- Two-player local multiplayer
- Responsive paddle controls
- Ball movement and collision detection
- Ball bouncing off the top and bottom walls
- Automatic score tracking
- Ball reset after a point is scored
- Ball direction changes based on where it hits the paddle
- Simple black-and-white Pong-style graphics
- Runs at a fixed **60 FPS**

## Gameplay

Each player controls one paddle and attempts to hit the ball past the opponent's paddle.

- The **left player** controls the paddle on the left side of the screen.
- The **right player** controls the paddle on the right side of the screen.
- The ball bounces off the top and bottom boundaries.
- When the ball hits a paddle, its horizontal direction reverses.
- The vertical velocity changes depending on where the ball hits the paddle.
- If the ball passes the left paddle, the right player scores.
- If the ball passes the right paddle, the left player scores.
- After a point is scored, the ball returns to the center and moves toward the player who conceded the point.

## Controls

| Player | Action | Key |
|---|---|---|
| Left Player | Move up | `W` |
| Left Player | Move down | `S` |
| Right Player | Move up | `↑` |
| Right Player | Move down | `↓` |

Both players can control their paddles simultaneously.

## Game Window

The game uses a window with the following dimensions:

- **Width:** 700 pixels
- **Height:** 500 pixels
- **Frame rate:** 60 FPS

The paddles are positioned near the left and right edges of the screen, while the ball starts at the center.

## Project Structure

```text
.
├── README.md
├── requirements.txt
└── src/
    └── pong/
        └── Solution_main.py
```

### `src/pong/pong.py`

Contains the complete game implementation, including:

- Pygame initialization
- Game window setup
- Paddle class
- Ball class
- Rendering functions
- Collision handling
- Paddle movement
- Score management
- Main game loop

### `requirements.txt`

Contains the Python packages required to run the game.

## How It Works

### Paddle

The game uses a `Paddle` class to represent each player's paddle.

Each paddle has:

- An `x` and `y` position
- A width and height
- A movement speed
- A color
- A method for drawing itself on the screen
- A method for moving up or down

The two paddles use the same dimensions but are positioned on opposite sides of the game window.

### Ball

The `Ball` class manages the ball's:

- Starting position
- Current position
- Radius
- Horizontal velocity
- Vertical velocity

The ball moves every frame according to its current velocity.

When the ball reaches the top or bottom of the game window, its vertical velocity is reversed, causing it to bounce.

### Paddle Collision

When the ball reaches a paddle, the game checks whether the ball is within the paddle's vertical range.

If a collision occurs:

1. The ball is repositioned so it does not overlap the paddle.
2. Its horizontal velocity is reversed.
3. Its vertical velocity is calculated based on where it hit the paddle.

Hitting the paddle near its center produces a more horizontal trajectory, while hitting closer to the top or bottom produces a steeper trajectory.

### Scoring

The game keeps separate scores for both players and displays them at the top of the screen.

If the ball moves beyond the left edge of the screen, the right player scores.

If the ball moves beyond the right edge of the screen, the left player scores.

The ball is then reset to the center of the screen and sent toward the player who lost the point.

## Installation

Make sure **Python 3** is installed on your system.

Clone or download the repository, then navigate to the project directory.

Install the required dependency with:

```bash
pip install -r requirements.txt
```

## Running the Game

From the project root directory, run:

```bash
python src/pong/Solution_main.py
```

The Pong window should open and the game will start immediately.

## Requirements

The project requires:

- Python 3
- Pygame

Install Pygame manually if needed:

```bash
pip install pygame
```

Or install all project dependencies using:

```bash
pip install -r requirements.txt
```

## Game Loop

The game continuously performs the following operations:

1. Limits the game to 60 frames per second.
2. Draws the current game state.
3. Processes Pygame events.
4. Reads the keyboard state.
5. Moves the paddles.
6. Moves the ball.
7. Checks for collisions.
8. Updates the score when the ball leaves the screen.
9. Resets the ball when a point is scored.

This process continues until the player closes the game window.

## Technologies Used

- **Python** — Programming language used to build the game.
- **Pygame** — Library used for graphics, keyboard input, game timing, and window management.

## Learning Objectives

This project demonstrates several fundamental game-development concepts:

- Object-oriented programming with Python classes
- Game loops
- Real-time keyboard input
- 2D coordinate systems
- Basic physics and velocity
- Collision detection
- Screen rendering
- Frame-rate control
- Event handling
- Score tracking
- Separating game logic into functions and classes

## Future Improvements

Possible additions to the game include:

- Add a start screen and pause menu
- Add sound effects for paddle and wall collisions
- Add background music
- Add a winning score or match-ending condition
- Add a single-player mode with an AI-controlled paddle
- Add difficulty levels
- Add customizable paddle and ball speeds
- Add randomized ball starting angles
- Add visual effects when a player scores
- Add a game-over screen
- Add improved graphics and animations
- Add support for different window sizes
- Add controller input

## License

This project is intended for educational and personal use. Add a license to the repository if you plan to distribute or modify the project publicly.
