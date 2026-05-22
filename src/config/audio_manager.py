from ursina import Audio
import random


class AudioManager:
    def __init__(self) -> None:
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

    def play_ambient_music(self) -> None:
        if self.current_music is not None:
            self.current_music.stop()
        self.current_music = Audio(
            self.ambiance_music, loop=True, autoplay=True
        )

    def play_sound(self, sound_path: str) -> None:
        if self.current_sound:
            self.current_sound.stop()
        self.current_sound = Audio(
            f"assets/sounds/{sound_path}", autoplay=True, ignore_paused=True
        )

    def play_random_ghost(self) -> None:
        if self.ghosts_sounds:
            sound_to_play = random.choice(self.ghosts_sounds)
            self.play_sound(sound_to_play)
