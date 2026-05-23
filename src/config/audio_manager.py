"""Sound and music management for the Pac-Man game."""

from ursina import Audio
import random


class AudioManager:
    """Play and control game audio: ambient music and sound effects."""

    def __init__(self) -> None:
        """Initialize volumes, sound paths, and playback state."""
        self.is_muted: bool = False
        self.global_volume: float = 0.7
        self.ambiance_music = (
            "assets/sounds/ambiances/yongbi-desert-metin2.mp3"
        )

        self.ghosts_sounds: list[str] = [
            "assets/sounds/ghost_moan.wav",
            "assets/sounds/ghost_attack.wav",
        ]
        self.player_sounds: list[str] = [
            "assets/sounds/player_walk.wav",
            "assets/sounds/player_hit.wav",
        ]

        self.current_music: Audio | None = None
        self.current_sound: Audio | None = None

    def toggle_mute(self) -> None:
        """Toggle global mute on or off."""
        self.is_muted = not self.is_muted

        if self.current_music:
            self.current_music.volume = 0 if self.is_muted else 1

    def play_ambient_music(self) -> None:
        """Start or restart the looping ambient music track."""
        if self.current_music is not None:
            self.current_music.stop()
        self.current_music = Audio(
            self.ambiance_music,
            loop=True,
            autoplay=True,
            volume=0.0 if self.is_muted else self.global_volume,
            ignore_pause=True,
        )

    def set_volume(self, volume_percent: int) -> None:
        """Set the global volume from a 0–100 integer percentage."""
        self.global_volume = volume_percent / 100.0

        if self.current_music:
            self.current_music.volume = self.global_volume

    def play_sound(self, sound_path: str) -> None:
        """Play a one-shot sound effect at the current global volume."""
        if self.is_muted:
            return
        if self.current_sound:
            self.current_sound.stop()
        self.current_sound = Audio(
            f"assets/sounds/{sound_path}",
            autoplay=True,
            ignore_paused=True,
            volume=self.global_volume,
        )

    def play_random_ghost(self) -> None:
        """Play a random ghost sound effect."""
        if self.ghosts_sounds:
            sound_to_play = random.choice(self.ghosts_sounds)
            self.play_sound(sound_to_play)
