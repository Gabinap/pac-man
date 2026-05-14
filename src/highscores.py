import json

from src.game_config import GameConfig


class Highscores:
    def __init__(self, gcf: GameConfig) -> None:
        self.gcf = gcf

    def get_top_scores(self) -> list[tuple[str, int]]:
        highscores: list[tuple[str, int]] = []
        try:
            with open(self.gcf.highscore_filename, "r") as file:
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
                f"Info: '{self.gcf.highscore_filename}' not found. "
                "Starting fresh."
            )
            return highscores
        except json.JSONDecodeError as e:
            print(f"Error loading scores: JSON is corrupted ({e})")
            return highscores

        except Exception as e:
            print(f"Unexpected error loading scores: {e}")
            return highscores
