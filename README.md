# Space Shooter (Pygame)

A fast-paced top-down space shooter built with Python + Pygame.

## Quick Start

### 1) Requirements

- Python 3.x
- `pygame`

### 2) Install dependencies

If you already have a virtual environment, activate it first.

```bash
pip install pygame
```

### 3) Run the game

From the project folder:

```bash
python space_shooter.py
```

## Controls

- **W / A / S / D**: Move ship
- **Mouse**: Aim
- **Left Mouse Click**: Shoot (when Auto-Fire is OFF)
- **F**: Toggle Auto-Fire
- **M**: Toggle sound
- **ESC**: Pause (during gameplay)
- **SPACE**: Start (from menu) / Restart (after game over)

## Gameplay notes

- Defeat enemies to increase your score.
- Power-ups can drop during gameplay (e.g., rapid fire, shield, health).
- A boss appears after enough kills.

## Troubleshooting

### No sound / audio errors

- If you get an audio device error, try closing other apps using audio and run again.
- You can toggle sound in-game with **M**.

### `ModuleNotFoundError: No module named 'pygame'`

Install Pygame:

```bash
pip install pygame
```

## Other scripts in this folder

- `snake.py`: A separate Snake game.
- `space_shooter.py`: The Space Shooter game (main).
