"""Read/write the JSON highscores file declared in the game config."""

import json

from src.game_config import GameConfig


class Highscores:
    """Load, sort and persist player highscores from a JSON file."""

    def __init__(self, config: GameConfig) -> None:
        self.config = config

    def get_top_scores(self) -> list[tuple[str, int]]:
        highscores: list[tuple[str, int]] = []
        try:
            with open(self.config.highscore_filename, "r") as file:
                parsed_json = json.load(file)

                if isinstance(parsed_json, list):
                    valid_scores = []

                    for entry in parsed_json:
                        if (
                            isinstance(entry, dict)
                            and "name" in entry
                            and isinstance(entry["name"], str)
                            and "score" in entry
                            and isinstance(entry["score"], int)
                        ):

                            valid_scores.append(
                                (entry["name"], entry["score"])
                            )
                        else:
                            print(f"Warning: Invalid entry ignored: {entry}")

                    highscores = sorted(
                        valid_scores,
                        key=lambda item: item[1],
                        reverse=True,
                    )
                    return highscores
                else:
                    print(
                        "Error: The highscores file must be"
                        " a JSON list of dictionaries."
                    )
                    return highscores

        except FileNotFoundError:
            print(
                f"Info: '{self.config.highscore_filename}' not found. "
                "Starting fresh."
            )
            return highscores
        except json.JSONDecodeError as e:
            print(f"Error loading scores: JSON is corrupted ({e})")
            return highscores

        except Exception as e:
            print(f"Unexpected error loading scores: {e}")
            return highscores

    def add_score(self, player_name: str, score: int) -> str:
        current_scores = self.get_top_scores()

        current_scores.append((player_name, score))
        data_to_save: list[dict[str, str | int]] = []
        for name, score in current_scores:
            data_to_save.append({"name": name, "score": score})
        try:
            with open(
                self.config.highscore_filename, "w", encoding="utf-8"
            ) as file:
                json.dump(data_to_save, file, indent=4)
            return f"Score added for {player_name}"
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
