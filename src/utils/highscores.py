"""Read/write the JSON highscores file declared in the game config.

In-memory cache: the file is read once and reused for both menu rendering
and ``add_score``. Writes update the cache and the file together. The
on-disk list is capped at ``_MAX_ENTRIES`` so the file doesn't grow
unbounded over a long-running save profile.
"""

import json

from src.config.game_config import GameConfig

_MAX_ENTRIES: int = 10


class Highscores:
    """Load, sort and persist player highscores from a JSON file."""

    def __init__(self, config: GameConfig) -> None:
        """Initialize the manager with the config holding the file path."""
        self.config = config
        self._cache: list[tuple[str, int]] | None = None

    def get_top_scores(self) -> list[tuple[str, int]]:
        """Return the sorted highscores list; load from disk on first call."""
        if self._cache is not None:
            return self._cache
        self._cache = self._load_from_disk()
        return self._cache

    def _load_from_disk(self) -> list[tuple[str, int]]:
        """Read, validate, sort, and return scores from the JSON file."""
        try:
            with open(self.config.highscore_filename, "r") as file:
                parsed_json = json.load(file)
        except FileNotFoundError:
            print(
                f"Info: '{self.config.highscore_filename}' not found. "
                "Starting fresh."
            )
            return []
        except json.JSONDecodeError as e:
            print(f"Error loading scores: JSON is corrupted ({e})")
            return []
        except OSError as e:
            print(f"Error reading scores: {e}")
            return []

        if not isinstance(parsed_json, list):
            print(
                "Error: The highscores file must be"
                " a JSON list of dictionaries."
            )
            return []

        valid: list[tuple[str, int]] = []
        for entry in parsed_json:
            if (
                isinstance(entry, dict)
                and isinstance(entry.get("name"), str)
                and isinstance(entry.get("score"), int)
            ):
                valid.append((entry["name"], entry["score"]))
            else:
                print(f"Warning: Invalid entry ignored: {entry}")

        valid.sort(key=lambda item: item[1], reverse=True)
        return valid

    def add_score(self, player_name: str, score: int) -> str:
        """Append, sort, cap at 10, persist to disk, return a message."""
        scores = list(self.get_top_scores())
        scores.append((player_name, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        scores = scores[:_MAX_ENTRIES]

        data_to_save = [
            {"name": name, "score": s} for name, s in scores
        ]
        try:
            with open(
                self.config.highscore_filename, "w", encoding="utf-8"
            ) as file:
                json.dump(data_to_save, file, indent=4)
        except PermissionError:
            return (
                "Error: no permission to write "
                f"on file {self.config.highscore_filename}"
            )
        except OSError:
            return (
                "Error: can't write to this file  "
                f"on file {self.config.highscore_filename}"
            )
        self._cache = scores
        return f"Score added for {player_name}"
