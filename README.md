# 🎮 Game Development in Python

> A growing Python/Pygame game-development portfolio focused on arcade gameplay, real-time physics, AI systems, procedural effects, modular architecture, and interactive game design.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/Ghostofzenin08/Game--Development-In-Python)

---

## 🌌 Project Overview

**Game Development in Python** is my personal game-development portfolio built with **Python and Pygame**.

The repository documents my progression from basic game programming toward more structured game-engineering concepts, including:

- 🎮 Real-time 2D gameplay
- 🧠 Reactive AI systems
- ⚙️ Object-Oriented Programming
- 🏗️ Modular game architecture
- 💥 Collision detection and physics
- ✨ Procedural visual effects
- 🔊 Procedural audio synthesis
- 🕹️ Multiple game modes
- ⚡ Power-up systems
- 🎯 Game-state management
- 🧪 Testable and maintainable game components

The project is continuously evolving as new mechanics, systems, and games are added.

---

## 🚀 Featured Games

| Game | Genre | Main Concepts |
|---|---|---|
| 🚀 **Galaxy Shooters** | 2D Space Combat | Reactive AI, power-ups, projectiles, shields, VFX, audio |
| 🏓 **Enhanced Pong** | Arcade / Sports | Physics, AI, procedural audio, power-ups, game states |

---

# 🚀 Galaxy Shooters

**Galaxy Shooters** is a fast-paced 2D space combat game featuring starfighters, laser projectiles, reactive AI, health and shield mechanics, power-ups, visual effects, and a dedicated audio system.

The game supports both **Player vs AI** and **local 2-player** gameplay.

### 🌟 Features

#### 🤖 Reactive AI

The AI opponent can:

- Track the player's position
- React to incoming projectiles
- Attempt projectile avoidance
- Search for available power-ups
- Move toward useful power-ups
- Manage its firing behaviour

#### 🛡️ Health & Shield System

- Dynamic health bars
- Damage detection
- Temporary protective shields
- Health restoration power-ups

#### ✨ Visual Effects

The game includes procedural and runtime-generated effects such as:

- Glowing laser projectiles
- Muzzle flashes
- Explosion effects
- Shockwaves
- Particle-style impact effects

#### ⚡ Power-Up System

| Power-Up | Effect |
|---|---|
| ⚡ **RAPID** | Increases firing rate |
| 🛡️ **SHIELD** | Absorbs incoming damage |
| ❤️ **HEALTH** | Restores health |
| ✨ **DOUBLE** | Enables dual laser fire |
| 💨 **SPEED** | Increases movement speed |

### 🎮 Controls

| Action | Player 1 | Player 2 |
|---|---|---|
| Move Up | `W` | `↑` |
| Move Down | `S` | `↓` |
| Move Left | `A` | `←` |
| Move Right | `D` | `→` |
| Fire | `Left Ctrl` | `Right Ctrl` |

### Menu Controls

| Key | Action |
|---|---|
| `1` | Player vs AI |
| `2` | Local 2-Player |
| `Enter` / `Space` | Start |
| `R` | Rematch |
| `Esc` | Return to menu |

### 🏗️ Architecture

```text
GalaxyShootersGame
│
├── Spaceship
│   ├── Player
│   └── AI
│
├── Laser
├── PowerUp
├── LaserSpriteFactory
├── MuzzleFlash
├── Explosion
└── AudioManager
```

This structure separates gameplay entities, AI behaviour, effects, and audio responsibilities instead of putting the entire game into one large script.

---

# 🏓 Enhanced Pong

**Enhanced Pong** is an expanded version of the classic Pong game rebuilt with modular architecture and additional gameplay systems.

The project focuses heavily on physics, procedural audio, game-state management, and reusable components.

### 🌟 Features

- 🧠 Single-player AI mode
- 👥 Local 2-player mode
- 🌀 Dynamic ball spin
- 💨 Ball trail / motion effect
- ⚡ Gameplay power-ups
- 🏆 Match-based scoring
- ⏱️ Serve countdown
- 🔊 Runtime-generated sound effects
- 🎯 Modular entity architecture
- 🎮 Complete game-state flow

### ⚡ Power-Ups

| Power-Up | Effect |
|---|---|
| `+` Grow | Increases paddle height |
| `S` Slow | Reduces ball speed |

### 🔊 Procedural Audio

Enhanced Pong does not depend on external sound files for its basic game effects.

The project generates sound waves at runtime using mathematical sine-wave synthesis.

The audio system produces effects for:

- Paddle hits
- Wall collisions
- Scoring
- Power-up collection

### 🧩 Modular Structure

```text
Pong
│
├── config.py
│   └── Configuration and gameplay constants
│
├── entities.py
│   └── Paddle, Ball, PowerUp and Flash
│
├── audio.py
│   └── Procedural sound synthesis
│
├── game.py
│   └── Game controller and state machine
│
├── pong.py
│   └── Main entry point
│
└── Solution_main.py
    └── Alternative launcher
```

---

# 🌐 Project Website

The project also has a dedicated website containing information about the games, documentation, contribution information, and project resources.

### 🎮 Game Development Website

**https://game-development-in-python.vercel.app/**

The website currently showcases **Galaxy Shooters**, including game visuals, technical information, developer information, contribution instructions, and desktop installation instructions.

> 🌐 **Browser version:** The website currently lists the browser/WebAssembly edition as **coming soon**. The playable desktop edition is available through the Python/Pygame project.

---

# 📂 Repository Structure

```text
Game--Development-In-Python/
│
├── .github/
│   └── workflows/
│
├── .vscode/
│
├── src/
│   │
│   ├── Galaxy_shooters/
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   │   ├── background_GS.png
│   │   │   │   ├── red_spaceship.png
│   │   │   │   └── yellow_spaceship.png
│   │   │   │
│   │   │   └── sounds/
│   │   │       ├── background_GS.mp3
│   │   │       ├── damage_GS.mp3
│   │   │       ├── laser_GS.mp3
│   │   │       └── victory_GS.mp3
│   │   │
│   │   ├── game.py
│   │   ├── README_.md
│   │   └── requirements.txt
│   │
│   └── Pong/
│       ├── audio.py
│       ├── config.py
│       ├── entities.py
│       ├── game.py
│       ├── pong.py
│       ├── Solution_main.py
│       ├── README.md
│       └── requirements.txt
│
├── tests/
├── .gitignore
├── LICENSE
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Ghostofzenin08/Game--Development-In-Python.git

cd Game--Development-In-Python
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

For Galaxy Shooters:

```bash
pip install -r src/Galaxy_shooters/requirements.txt
```

For Pong:

```bash
pip install -r src/Pong/requirements.txt
```

Or install Pygame directly:

```bash
pip install pygame>=2.5.0
```

---

# 🕹️ Running the Games

## 🚀 Galaxy Shooters

From the repository root:

```bash
python src/Galaxy_shooters/game.py
```

## 🏓 Enhanced Pong

```bash
python src/Pong/pong.py
```

Alternative launcher:

```bash
python src/Pong/Solution_main.py
```

---

# 🧠 Technical Concepts

This repository is being developed around several important game-programming and software-engineering concepts.

### Object-Oriented Programming

Game entities are separated into classes with their own data and behaviour.

### Finite State Machines

Games use structured states such as:

```text
Menu
  ↓
Start
  ↓
Countdown
  ↓
Playing
  ↓
Game Over
  ↓
Rematch / Menu
```

### Real-Time Game Loops

The games target a consistent **60 FPS** update and rendering cycle.

### Collision Detection

Gameplay systems handle interactions between:

- Players
- Projectiles
- Walls
- Power-ups
- Game boundaries

### Reactive AI

Galaxy Shooters includes AI logic that reacts to player movement, projectiles, and available power-ups.

### Procedural Generation

Several visual and audio effects are generated programmatically instead of relying entirely on pre-made assets.

### Modular Architecture

The projects are progressively being divided into smaller components to improve:

- Maintainability
- Reusability
- Debugging
- Testing
- Future expansion

---

# 🧪 Testing

The repository also includes a `tests/` directory for automated testing and future test coverage.

As the projects become more complex, testing will be expanded to cover:

- Game entities
- Physics calculations
- Collision behaviour
- Power-up logic
- Game-state transitions
- Utility functions

---

# 🛠️ Development Roadmap

The repository is still under active development.

### Planned Improvements

- [ ] Settings menu
- [ ] Volume controls
- [ ] Key remapping
- [ ] Multiple AI difficulty levels
- [ ] Additional power-ups
- [ ] Improved enemy behaviour
- [ ] More advanced VFX
- [ ] Network multiplayer experiments
- [ ] Additional arcade games
- [ ] 2D top-down roguelike project
- [ ] Improved automated test coverage
- [ ] Browser/WebAssembly version of Galaxy Shooters

---

# 🎯 Learning Goals

This repository is more than a collection of games. It is also a learning journey toward professional software and game development.

The main goals are to improve my understanding of:

```text
Python
   ↓
Object-Oriented Programming
   ↓
Game Loops & Real-Time Systems
   ↓
Physics & Collision Detection
   ↓
AI Behaviour
   ↓
Procedural Graphics & Audio
   ↓
Software Architecture
   ↓
Testing
   ↓
Deployment
   ↓
Advanced Game Development
```

---

# 🌐 Deployment

The project has a dedicated Vercel-hosted website:

**Game Development in Python**

https://game-development-in-python.vercel.app/

The website acts as the presentation and documentation layer for the game-development portfolio, while the GitHub repository contains the source code and assets.

**Thanks to..**
 Parth - https://github.com/parthongit89

---

# 🤝 Contributing

Contributions and suggestions are welcome.

### Development workflow

```bash
git checkout -b feature/your-feature-name
```

Make your changes, test them locally, and submit a pull request.

Possible contribution areas include:

- New gameplay mechanics
- AI improvements
- New power-ups
- Physics improvements
- Visual effects
- Audio systems
- New games
- Testing
- Documentation

---

# 👨‍💻 Developer

### Harshal 

**GitHub:** [@Ghostofzenin08](https://github.com/Ghostofzenin08)

**Project Website:** https://game-development-in-python.vercel.app/

Interested in:

- Python
- Game Development
- Pygame
- Software Architecture
- Real-Time Systems
- AI Behaviour
- Physics Simulation
- Procedural Graphics
- Game Engineering

---

# 📜 License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for more information.

---

## ⭐ Support the Project

If you find this project interesting:

- ⭐ Star the repository
- 🍴 Fork the project
- 🐛 Report issues
- 💡 Suggest new features
- 🔧 Contribute improvements

---

> **Built with Python + Pygame — one game at a time. 🎮🚀**
