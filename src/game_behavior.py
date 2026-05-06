"""Core game logic and state management.

Manages the game loop state: player movement, ghost AI,
collision detection, scoring, life management, level
transitions, input buffering, and the highscore system.
Receives a GameConfig on initialization and exposes an
update() method called every frame by visualization.
"""
