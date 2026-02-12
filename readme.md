🚀 Invader Swarm – Enhanced Edition

A classic space-invader arcade game built with Python + Arcade, featuring progressive difficulty, power-ups, boss fights, and particle effects.

🎮 Download & Play (Windows)

Invader Swarm v1.0 – 64-bit Executable
➡️ Download and run — no installation required

🕹️ Features
Core Gameplay

5 Enemy Types with unique behaviors

Boss battles every 5 waves

Progressive wave difficulty

Score multiplier system

Local high-score saving

Power-Ups

🛡️ Shield – Temporary invincibility

❤️ Extra Life

🔫 Spread Shot

💣 Nuke – Clear all enemies

⚡ Rapid Fire

Visuals & Audio

Particle explosions

Screen shake effects

Full sound effects

Dynamic backgrounds

Auto-scaling sprites

🎯 Controls
Key	Action
← → / A D	Move
↑ ↓ / W S	Vertical move
SPACE	Fire
P	Pause
R	Restart
ESC	Exit
💻 System Requirements

Windows 10/11 (64-bit)

2 GB RAM

DirectX 10 GPU

100 MB storage

🛠️ Build from Source
git clone https://github.com/yourusername/invader_swarm.git
cd invader_swarm
pip install arcade pyinstaller
python invader_swarm.py

Create EXE
pyinstaller --onefile --windowed ^
--add-data "assets/images;assets/images" ^
--add-data "assets/sounds;assets/sounds" ^
--add-data "high_scores.json;." ^
invader_swarm.py

📁 Structure
invader_swarm/
├── assets/
│   ├── images/
│   └── sounds/
├── invader_swarm.py
├── high_scores.json
└── README.md
