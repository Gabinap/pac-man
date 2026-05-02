"""Configuration file parser for the Pac-Man game.

Reads and validates the JSON configuration file passed as
a command-line argument. Handles comment stripping, type
checking, value clamping, and unknown key ignoring.
Returns a populated GameConfig instance on success, or
exits cleanly with a descriptive message on failure.
"""