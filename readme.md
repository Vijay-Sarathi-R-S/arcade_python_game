Invader Swarm - Enhanced Edition

A classic space invader-style arcade game built with Python and Arcade, featuring progressive difficulty, power-ups, boss battles, and stunning particle effects!

🎮 Download & Play
Windows Users
⬇️ Download Invader Swarm v1.0 (64-bit executable)

No installation required! Just download and run.

🕹️ Game Features
Core Gameplay
5 Unique Enemy Types - Green, Red, Extra, Alien, and Drifters with unique behaviors and attack patterns

Epic Boss Battles - Face powerful bosses every 5th wave with multiple attack patterns

5 Power-ups - Collect and activate:

🛡️ Shield - Temporary invincibility

❤️ Extra Life - +1 life

🔫 Spread Shot - Triple bullet spread

💣 Nuke - Instantly clear all enemies

⚡ Rapid Fire - Increased firing rate

Visual & Audio
Particle Explosion System - Satisfying destruction effects

Screen Shake - Impact feedback when taking damage

Full Sound Effects - Shoot, explode, power-up, boss entrance, and game over

Dynamic Backgrounds - Random background selection

Auto-scaling Sprites - Perfect rendering at any resolution

Progression System
Wave System - Increasing difficulty as you advance

Score Multiplier - Chain kills to multiply your score (up to 4x)

High Score Persistence - Your best scores are saved locally

Progressive Difficulty - Enemies get faster and more aggressive each wave

🎯 How to Play
Controls
Key	Action
← → or A D	Move left/right
↑ ↓ or W S	Move up/down
SPACE	Fire weapon
P	Pause/Resume game
R	Restart (game over screen)
ESC	Return to game over / Exit
Gameplay Tips
Chain kills to maintain your score multiplier

Red aliens shoot faster - prioritize them!

Extra aliens drop power-ups more frequently

Alien aliens split into drifters when destroyed

Save nuke power-ups for emergency situations

Bosses have multiple attack patterns - learn to dodge!

📋 System Requirements
OS: Windows 10/11 (64-bit)

Processor: 1.5 GHz or faster

Memory: 2 GB RAM

Graphics: DirectX 10 compatible GPU

Storage: 100 MB available space

No additional software required!

🛠️ Building from Source
Prerequisites
Python 3.8 or higher

pip (Python package installer)

Setup
Clone the repository

bash
https://github.com/Vijay-Sarathi-R-S/arcade_python_game/new/main
cd invader_swarm
Create a virtual environment (recommended)

bash
python -m venv env
env\Scripts\activate  # On Windows
Install dependencies

bash
pip install arcade pyinstaller
Run the game

bash
python invader_swarm.py
Creating Executable
Using PyInstaller with spec file:

bash
pyinstaller invader_swarm.spec
Or using direct command:

bash
pyinstaller --onefile --windowed ^
--add-data "assets/images/background/*.png;assets/images/background" ^
--add-data "assets/images/bosses/*.png;assets/images/bosses" ^
--add-data "assets/images/enemies/*.png;assets/images/enemies" ^
--add-data "assets/images/player/*.png;assets/images/player" ^
--add-data "assets/images/powerups/*.png;assets/images/powerups" ^
--add-data "assets/sounds/*.mp3;assets/sounds" ^
--add-data "high_scores.json;." ^
invader_swarm.py
The executable will be created in the dist folder.

📁 Project Structure
text
invader_swarm/
├── assets/
│   └── images/
│       ├── background/     # Background images
│       ├── bosses/         # Boss sprites
│       ├── enemies/        # Enemy sprites
│       ├── player/         # Player ship sprite
│       └── powerups/       # Power-up sprites
│   └── sounds/            # MP3 sound effects
├── invader_swarm.py       # Main game file
├── invader_swarm.spec     # PyInstaller spec file
├── high_scores.json       # Local high scores
├── README.md             # This file
└── requirements.txt      # Python dependencies
⚠️ Troubleshooting
Common Issues
1. Game crashes on startup

Ensure all asset folders exist in the correct locations

Run from command line to see error messages

2. No sounds or images in executable

Verify PyInstaller is including all assets (check the spec file)

Try running the executable from command prompt to see missing file errors

3. Antivirus false positive

This is common with PyInstaller executables

Add the file to your antivirus exceptions

Or build from source yourself

4. Performance warnings

The draw_text warning is normal and doesn't affect gameplay

Consider using arcade.Text objects for better performance
