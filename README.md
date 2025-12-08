# Cake Catcher - Hand Tracking Game

A Python game using Pygame, OpenCV, and Mediapipe for hand tracking.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python main.py
```

2. Position your hand in front of the webcam
3. Move your index finger left/right to control the plate
4. Catch GOOD items (green circles) for +10 points
5. Avoid BAD items (red circles with X) which deduct -15 points
6. Catch SPECIAL items (gold circles) for +50 points and special effects!
7. Game lasts 60 seconds - get the highest score!

## Controls

- **Index Finger Movement**: Control plate position
- **W Key**: Toggle webcam preview
- **R Key**: Restart game (after game over)
- **ESC**: Quit game

## Features

- Real-time hand tracking using Mediapipe
- Smooth plate movement with interpolation
- Difficulty ramping every 15 seconds
- Visual score feedback with popups
- Screen shake effect for special items
- 60-second timed gameplay

## Project Structure

```
Cake_Catcher/
├── main.py                 # Main game loop
├── game/
│   ├── __init__.py
│   ├── hand_tracker.py    # Mediapipe hand tracking
│   ├── player.py          # Plate/player logic
│   ├── item.py            # Falling items
│   ├── game_manager.py    # Game state & logic
│   └── utils.py           # Utilities & constants
├── assets/
│   ├── images/            # Placeholder sprites
│   └── sounds/            # Placeholder sounds
└── requirements.txt
```
