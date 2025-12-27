# Space Shooter (Pygame)

A fast-paced top-down space shooter built with **Python** + **Pygame**.

## Quick Start

### Requirements

- Python 3
- Pygame

### Install

```bash
pip install pygame
```

### Run

```bash
python space_shooter.py
```

## Controls

### Gameplay

- `W` `A` `S` `D`: Move ship
- Mouse: Aim
- Left Mouse Click: Shoot (when Auto-Fire is OFF)
- `F`: Toggle Auto-Fire
- `M`: Toggle Sound
- `ESC`: Pause / Resume

### Menu / Game Over

- `SPACE`: Start / Restart
- `ESC`: Quit (from menu) / Back to menu (after game over)

## What’s in the game

- Waves of enemies (including shooter-type enemies)
- Power-ups (Rapid Fire, Shield, Health)
- Boss fights after enough kills
- Procedural sound effects (toggle with `M`)

## Troubleshooting

### `ModuleNotFoundError: No module named 'pygame'`

```bash
pip install pygame
```

### Sound issues

- Try toggling sound in-game with `M`.
- If your system has no audio device available, Pygame audio init may fail depending on configuration.

## Other scripts

- `space_shooter.py`: Space Shooter (main)
- `snake.py`: Separate Snake game
