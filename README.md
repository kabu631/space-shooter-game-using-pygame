# 🚀 Space Shooter: Complete Edition

A high-octane, arcade-style top-down shooter built with **Python** and **Pygame**. This edition features advanced AI, procedural sound generation, and a dynamic wave system.

## ✨ Features

* **Dynamic Combat**: $360^{\circ}$ mouse-aiming with physics-normalized movement.
* **Procedural Audio**: Real-time sound synthesis for lasers, explosions, and power-ups—no external audio files needed.
* **Tactical AI**: Includes "Shooter" enemies that maintain distance and a multi-phase Boss with homing missiles and circular burst patterns.
* **Combo System**: Earn higher scores by maintaining kill streaks (multiplier: $1 + \text{combo} \times 0.1$).
* **Power-ups**: Collect Rapid Fire, Shields, and Health drops from defeated enemies.
* **Visual Engine**: Custom particle system for explosions and engine trails, plus a parallax twinkling starfield.

## 🎮 Controls

### Gameplay
- **W, A, S, D**: Move ship
- **Mouse**: Aim direction
- **Left Click**: Shoot (Manual Mode)
- **F**: Toggle Auto-Fire
- **M**: Toggle Sound
- **ESC**: Pause / Resume

### Menu & Game Over
- **SPACE**: Start / Restart
- **ESC**: Quit to Menu

## 🛠️ Installation

1.  **Requirement**: Python 3.x and Pygame.
2.  **Install Dependencies**:
    ```bash
    pip install pygame
    ```
3.  **Run Game**:
    ```bash
    python space_shooter.py
    ```

## 📈 Technical Details
- **Physics**: Uses vector math for projectile tracking and movement.
- **State Management**: Robust transitions between Menu, Play, Pause, and Game Over states.
- **Data**: Tracks lifetime statistics including total kills and bosses defeated using Python dataclasses.

## 🗺️ Roadmap
- [ ] **Sprite Integration**: Replace vector shapes with the alien pixel art.
- [ ] **Weapon Upgrades**: Add different firing modes like spread-shot and laser beams.
- [ ] **Leaderboard**: Implement a local file-based high score saving system.
- [ ] **Battle Royale**: Will change the game environment as a battle royale 0f 8-10 players with better graphics, characters and weapons.

---
*Developed with love, developed for fun*
