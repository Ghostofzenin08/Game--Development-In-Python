# 🚀 Galaxy Shooters

**Galaxy Shooters** is a 2D space battle arcade game built with **Python and Pygame**. The game features fast-paced spaceship combat, an AI opponent, two-player mode, power-ups, laser effects, explosions, background music, and sound effects.

This project was developed as part of my **Game Development in Python** portfolio to practice object-oriented programming, game loops, collision detection, AI behavior, visual effects, audio management, and game-state handling.

---

## 🎮 Features

- 🚀 Player spaceship movement
- 🤖 Player vs AI game mode
- 👥 Two-player local game mode
- 🔫 Laser-based combat
- ❤️ Health system
- ⚡ Rapid-fire power-up
- 🛡️ Shield power-up
- ❤️ Health recovery power-up
- ✨ Double-shot power-up
- 💨 Speed boost power-up
- 💥 Explosion effects
- ✨ Muzzle-flash effects
- 🌟 Glowing laser effects
- 🤖 AI movement and laser dodging
- 🎯 AI power-up collection
- 🎵 Background music
- 🔊 Laser, damage, and victory sound effects
- 🖥️ Main menu and game-over screens
- 🔄 Restart functionality
- ⏱️ Timed power-up effects
- 🧩 Object-oriented game architecture

---

## 🕹️ Game Modes

### Player vs AI

Fight against the computer-controlled spaceship.

- **Yellow spaceship:** Player
- **Red spaceship:** AI

The AI can follow the opponent, avoid incoming lasers, collect power-ups, and fire automatically.

### Two Players

Play locally with two players on the same keyboard.

- **Player 1:** Yellow spaceship
- **Player 2:** Red spaceship

---

## 🎮 Controls

### Player 1

| Action | Key |
|---|---|
| Move Up | `W` |
| Move Down | `S` |
| Move Left | `A` |
| Move Right | `D` |
| Fire | `Left Ctrl` |

### Player 2

| Action | Key |
|---|---|
| Move Up | `↑` |
| Move Down | `↓` |
| Move Left | `←` |
| Move Right | `→` |
| Fire | `Right Ctrl` |

### Menu

| Action | Key |
|---|---|
| Player vs AI | `1` |
| Two Players | `2` |
| Start Game | `Enter` / `Space` |
| Return to Menu | `Esc` |
| Restart | `R` |

---

## ⚡ Power-Ups

Power-ups periodically appear on the battlefield and provide temporary advantages.

| Power-Up | Effect |
|---|---|
| ⚡ **RAPID** | Increases firing speed and bullet capacity |
| 🛡️ **SHIELD** | Protects the spaceship from damage |
| ❤️ **+HEALTH** | Restores health |
| ✨ **DOUBLE** | Fires two lasers at once |
| 💨 **SPEED** | Increases spaceship movement speed |

Power-ups have limited lifetimes and temporary effects, making them an important part of the battle strategy.

---

## 🧠 AI System

The computer-controlled spaceship uses a basic reactive AI system.

The AI can:

- Track the player's vertical position
- Move toward useful positions
- Detect incoming lasers
- Attempt to dodge dangerous projectiles
- Search for nearby power-ups
- Collect available power-ups
- Fire automatically

---

## 🛠️ Technologies Used

- **Python 3**
- **Pygame**
- Object-Oriented Programming
- 2D game development
- Collision detection
- Game-state management
- Basic AI behavior
- Particle and visual effects
- Audio management

---

## 📂 Project Structure

```text
Galaxy-Shooters/
│
├── galaxy_shooters.py
│
├── assets/
│   ├── images/
│   │   ├── background_GS.png
│   │   ├── yellow_spaceship.png
│   │   └── red_spaceship.png
│   │
│   └── sounds/
│       ├── laser_GS.mp3
│       ├── damage_GS.mp3
│       ├── victory_GS.mp3
│       └── background_GS.mp3
│
└── README.md
```

> **Note:** Keep the `images` and `sounds` folders inside the expected `assets` directory so the game can load its resources correctly.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Ghostofzenin08/Game--Development-In-Python.git
```

### 2. Navigate to the Galaxy Shooters project

Navigate into the folder containing the Galaxy Shooters Python file.

### 3. Install Pygame

```bash
pip install pygame
```

Or:

```bash
python -m pip install pygame
```

### 4. Run the game

```bash
python galaxy_shooters.py
```

> Replace `galaxy_shooters.py` with the actual filename if you have named the Python file differently.

---

## 🏗️ Architecture

The game uses an object-oriented structure with dedicated classes for different systems.

### Core Classes

```text
GalaxyShootersGame
        │
        ├── Spaceship
        │      ├── Player
        │      └── AI
        │
        ├── Laser
        ├── PowerUp
        ├── Explosion
        ├── MuzzleFlash
        ├── LaserSpriteFactory
        └── AudioManager
```

This structure keeps gameplay entities, visual effects, audio, and game control separated into logical components.

---

## 🎨 Visual Effects

The game generates several visual effects directly through Pygame, including:

- Laser glow
- Laser trails
- Muzzle flashes
- Explosion shockwaves
- Power-up pulsing effects
- Shield glow
- Hit feedback

This allows the game to create dynamic effects without requiring a separate image asset for every visual effect.

---

## 🔊 Audio

The game includes separate audio resources for:

- Background music
- Laser firing
- Damage/hit effects
- Victory

An `AudioManager` class handles audio playback and background music.

---

## 🎯 Game Objective

Reduce the opponent's health to **zero** before they defeat you.

In Player vs AI mode:

> **Defeat the computer-controlled spaceship.**

In Two Player mode:

> **Defeat the opposing player.**

---

## 📈 Future Improvements

This project is actively being developed and will receive additional improvements over time.

Planned features may include:

- 🏆 Scoring system
- ⏸️ Pause functionality
- 🎚️ Settings menu
- 🔊 Audio controls
- 🤖 Multiple AI difficulty levels
- 🏅 High-score system
- 🎨 Additional visual effects
- 🚀 More spaceship/weapon variations
- 🌌 Additional arenas or backgrounds
- 📊 Improved game statistics

These features are **not part of the current version** and will be introduced through future updates.

---

## 📚 What I Learned

Through this project, I practiced:

- Python OOP
- Classes and objects
- Game loops
- Pygame event handling
- Collision detection
- Projectile systems
- Timed effects
- AI movement
- Keyboard input
- Audio management
- Asset management
- Visual effects
- Game-state management
- Structuring a larger Python project

---

## 🚧 Development Status

**Current Status: 🟢 Playable**

The current version includes the core gameplay loop and several gameplay systems. Additional features and refinements will be added progressively as part of the project's continued development.

---

## 👨‍💻 Author

**Harshal**

This project is part of my **Game Development in Python** portfolio, where I experiment with different game mechanics, programming concepts, and Pygame-based projects.

---

## ⭐ Project Goals

The goal of this project is not only to create a playable game, but also to continuously improve my:

- Python programming
- Game development skills
- Object-oriented design
- Problem-solving ability
- Software project organization

Future commits will progressively expand and polish the game.

---

## 📜 License

This project is intended for educational and portfolio purposes.
