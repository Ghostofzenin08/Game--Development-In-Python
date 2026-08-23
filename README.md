# 🎮 Game Development in Python

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.5.0%2B-green?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](https://github.com/Ghostofzenin08/Game--Development-In-Python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Welcome to the **Game Development in Python** repository! 🚀



This repository is a curated portfolio of 2D arcade games, real-time physics simulations, reactive AI systems, procedural audio/visual effects, and modular object-oriented game architectures engineered using **Python** and **Pygame**.

---


![Preview](/src/Galaxy_shooters/assets/images/image.png)

## 📑 Table of Contents

- [🎮 Featured Games Overview](#-featured-games-overview)
- [🚀 Galaxy Shooters](#-galaxy-shooters)
  - [Features](#-features)
  - [Power-Up System](#-power-up-system)
  - [Controls Reference](#-controls-reference)
  - [Architecture](#-architecture)
- [🏓 Enhanced Pong](#-enhanced-pong)
  - [Features](#-features-1)
  - [Procedural Audio Engine](#-procedural-audio-engine)
  - [Controls Reference](#-controls-reference-1)
  - [Modular Structure](#-modular-structure)
- [📂 Repository Structure](#-repository-structure)
- [⚙️ Installation & Setup](#️-installation--setup)
- [🕹️ Launching the Games](#️-launching-the-games)
- [🏗️ Software Architecture & Design Principles](#️-software-architecture--design-principles)
- [📈 Roadmap & Future Plans](#-roadmap--future-plans)
- [👨‍💻 Author & Connect](#-author--connect)
- [📜 License](#-license)

---

## 🎮 Featured Games Overview

| Game | Genre / Theme | Modes | Highlights |
| :--- | :--- | :--- | :--- |
| **[🚀 Galaxy Shooters](#-galaxy-shooters)** | Fast-Paced Space Combat | • Player vs AI<br>• 2-Player Local PvP | 5 dynamic power-ups, reactive laser-dodging AI, glowing laser shaders, muzzle flash, explosion shockwaves, audio manager |
| **[🏓 Enhanced Pong](#-enhanced-pong)** | Enhanced Classic Arcade | • Single Player vs AI<br>• 2-Player Local PvP | 100% procedural sine-wave audio synthesis, ball trail blur, spin-deflection physics, dynamic power-ups, match system |

---

## 🚀 Galaxy Shooters

**Galaxy Shooters** is a high-action 2D space duel game where two starfighters battle across territorial airspace with laser cannons, energy shields, and tactical drops.

### 🌟 Features

- **🤖 Intelligent Reactive AI**:
  - Automatically tracks opponent vertical coordinates.
  - Detects incoming enemy lasers and computes evasion trajectories to dodge danger.
  - Scans for battlefield power-ups and moves to collect them.
  - Automatically calculates optimal firing intervals.
- **🛡️ Dynamic Health & Shield System**:
  - Live animated health bars for both combatants.
  - Temporary energy barrier absorbs incoming projectile damage.
- **✨ Procedural Graphics & Shader Effects**:
  - Multi-layered glowing laser surfaces rendered in real time.
  - Directional muzzle flashes when blasters fire.
  - Expanding shockwave and particle blast effects on projectile impact.
- **🎵 Full Audio System**: Dedicated `AudioManager` handling background soundtrack, laser fire, impact explosions, and victory jingles.

### ⚡ Power-Up System

Power-ups spawn periodically on the battlefield with countdown lifetimes:

| Icon | Name | Color | Tactical Effect |
| :---: | :--- | :--- | :--- |
| ⚡ | **RAPID** | Cyan | Increases blaster fire rate and doubles max on-screen projectiles |
| 🛡️ | **SHIELD** | Blue | Deploys a protective force field absorbing incoming hits |
| ❤️ | **+HEALTH** | Green | Instantly repairs hull damage and restores lost health points |
| ✨ | **DOUBLE** | Pink | Upgrades weapon cannons to fire two synchronized laser beams |
| 💨 | **SPEED** | Orange | Increases thruster propulsion and movement speed |

### 🎮 Controls Reference

| Action | Player 1 (Yellow Ship) | Player 2 (Red Ship) | Menu Controls |
| :--- | :---: | :---: | :---: |
| **Move Up / Down** | `W` / `S` | `↑` / `↓` | `1` : Mode: Player vs AI |
| **Move Left / Right** | `A` / `D` | `←` / `→` | `2` : Mode: Two Players |
| **Fire Blaster** | `Left Ctrl` | `Right Ctrl` | `Enter` / `Space` : Start Game |
| **Game Over State** | — | — | `R` : Rematch \| `Esc` : Return to Menu |

### 🏛️ Architecture

```text
GalaxyShootersGame (Main Controller & Game Loop)
│
├── Spaceship (Base Entity)
│   ├── Player (Human Input Handler)
│   └── AI (State Evaluator & Auto-pilot)
│
├── Laser (Projectile Entity)
├── PowerUp (Spawn & Buff Lifecycles)
├── LaserSpriteFactory (In-Memory Glow Renderer)
├── MuzzleFlash & Explosion (Particle VFX)
└── AudioManager (Sound FX & Background Music)
```

---

## 🏓 Enhanced Pong

An engineered evolution of the timeless Pong arcade game rebuilt from the ground up with modular architecture, procedural sound synthesis, spin physics, and power-up modifiers.

### 🌟 Features

- **🔊 Pure Procedural Audio**: Generates all game sound effects dynamically at runtime without external audio assets.
- **🌀 Dynamic Spin & Deflection Physics**: Ball exit angle and vertical velocity dynamically scale based on impact point on the paddle and paddle velocity.
- **💨 Motion Blur & Trail Visuals**: Smooth queue-based alpha trail tracking the ball trajectory.
- **⚡ Interactive Power-Ups**:
  - `+` **Grow**: Extends paddle height by 1.5x for 6 seconds.
  - `S` **Slow**: Reduces ball speed back to baseline to recover control during fast rallies.
- **🏆 Complete Match State Machine**:
  - Start screen with mode selection.
  - 3-second serve countdowns between points.
  - Scoreboard tracking points to a winning score of 5.
  - Victory celebration screen with restart and quit keys.

### 🔊 Procedural Audio Engine

Unlike standard implementations that rely on external `.wav` or `.mp3` files, Enhanced Pong utilizes an internal procedural sound synthesizer (`audio.py`):

```python
# Procedural sine wave sound generation at runtime
rate = 22050
data = array("h", (
    int(9000 * math.sin(2 * math.pi * frequency * i / rate))
    for i in range(int(rate * duration))
))
pygame.mixer.Sound(buffer=data)
```

Generated sound profiles:
- **Paddle Hit:** High crisp ping (620 Hz, 70 ms)
- **Wall Bounce:** Deep bounce thud (300 Hz, 50 ms)
- **Score Point:** Low buzzer tone (180 Hz, 180 ms)
- **Power-Up Grab:** High energizing chime (900 Hz, 120 ms)

### 🎮 Controls Reference

| Action | Left Player (P1) | Right Player (P2 / AI) | System Navigation |
| :--- | :---: | :---: | :---: |
| **Move Paddle** | `W` (Up) / `S` (Down) | `↑` (Up) / `↓` (Down) | `1` : Single Player (vs AI) |
| **Select Mode** | — | — | `2` : Two Players Local |
| **Start / Serve** | — | — | `Space` / `Enter` : Start Game |
| **End of Match** | — | — | `R` : Play Again \| `Esc` : Exit |

### 🧩 Modular Structure

Pong is decoupled into independent, testable modules:
- `config.py` — Window dimensions, speeds, colors, and balance constants.
- `entities.py` — `Paddle`, `Ball`, `PowerUp`, and `Flash` data models.
- `audio.py` — Synthesized sound generator.
- `game.py` — `PongGame` state machine, collision coordinator, and renderer.
- `pong.py` / `Solution_main.py` — Executable entry points.

---

## 📂 Repository Structure

```text
Game--Development-In-Python/
│
├── .gitignore                              # Git exclusion rules
├── LICENSE                                 # MIT License
├── README.md                               # Root repository documentation
│
└── src/
    ├── Galaxy_shooters/                    # 🚀 Galaxy Shooters Project
    │   ├── assets/
    │   │   ├── images/                     # Sprite textures & backgrounds
    │   │   │   ├── background_GS.png
    │   │   │   ├── red_spaceship.png
    │   │   │   └── yellow_spaceship.png
    │   │   └── sounds/                     # Game audio assets
    │   │       ├── background_GS.mp3
    │   │       ├── damage_GS.mp3
    │   │       ├── laser_GS.mp3
    │   │       └── victory_GS.mp3
    │   ├── game.py                         # Galaxy Shooters main application
    │   ├── README_.md                      # Dedicated Galaxy Shooters documentation
    │   └── requirements.txt                # Galaxy Shooters dependencies
    │
    └── Pong/                               # 🏓 Enhanced Pong Project
        ├── audio.py                        # Procedural sound synthesis engine
        ├── config.py                       # Balance parameters & display settings
        ├── entities.py                     # Decoupled entity classes & physics
        ├── game.py                         # Game controller & state machine
        ├── pong.py                         # Direct entry-point script
        ├── Solution_main.py                # Main launcher wrapper
        ├── README.md                       # Dedicated Pong documentation
        └── requirements.txt                # Pong dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- **Python 3.8 or higher** installed on your system. Verify with:
  ```bash
  python --version
  ```

### 2. Clone the Repository
```bash
git clone https://github.com/Ghostofzenin08/Game--Development-In-Python.git
cd Game--Development-In-Python
```

### 3. Create a Virtual Environment (Recommended)

**Windows (PowerShell / Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install pygame>=2.5.0
```
*Or install via project requirements files:*
```bash
pip install -r src/Galaxy_shooters/requirements.txt
```

---

## 🕹️ Launching the Games

Run each game directly from the repository root:

### 🚀 Play Galaxy Shooters
```bash
python src/Galaxy_shooters/game.py
```

### 🏓 Play Enhanced Pong
```bash
python src/Pong/pong.py
```
*(Alternative launcher: `python src/Pong/Solution_main.py`)*

---

## 🏗️ Software Architecture & Design Principles

- **Object-Oriented Programming (OOP)**: Clear separation of entity attributes, behavior methods, and rendering logic.
- **Finite State Machines (FSM)**: Structured lifecycle management (`start` ➔ `countdown` ➔ `playing` ➔ `game_over`).
- **Procedural Generation**: In-memory visual asset synthesis using `pygame.SRCALPHA` and procedural mathematical audio synthesis via sine wave byte buffers.
- **Deterministic 60 FPS Game Loop**: Consistent collision detection, physics updates, and smooth frame rendering.
- **Reactive AI Agents**: Real-time position tracking, projectile trajectory avoidance, and autonomous decision loops.

---

## 📈 Roadmap & Future Plans

- [ ] Add interactive settings menu (volume sliders, key remapping) to Galaxy Shooters.
- [ ] Multi-level AI difficulty settings (Easy, Medium, Hard, Unbeatable).
- [ ] Additional power-up types (Laser Turrets, EMP Blasts, Multi-Ball).
- [ ] Network multiplayer prototype using Python Sockets / UDP.
- [ ] New upcoming game: 2D Top-Down Roguelike Dungeon Crawler.

---

## 👨‍💻 Author & Connect

**Harshal**
- **GitHub:** [@Ghostofzenin08](https://github.com/Ghostofzenin08)
- **Portfolio Goal:** Mastering Python software architecture, real-time algorithms, and creative game engineering.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
