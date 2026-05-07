from ursina import Entity, Text, Button, color, destroy
from typing import Callable
import json

from src.game_config import GameConfig
from src.views.base import BaseView


class HighscoresView(BaseView):
    def __init__(
        self, gcf: GameConfig, back_callback: Callable[[], None]
    ) -> None:
        super().__init__()

        self.gcf = gcf
        self.back_callback = back_callback
        Text(
            text="- Best scores -",
            origin=(0, 0),
            y=0.35,
            scale=3,
            color=color.yellow,
            parent=self,
        )

        self.btn_back = Button(
            text="Back",
            color=color.gray,
            scale=(0.2, 0.08),
            y=-0.4,
            parent=self,
        )
        self.btn_back.on_click = self.back_callback

        self.scores_container = Entity(parent=self)

    def on_enter(self) -> None:
        self.load_and_display_scores()

    def load_and_display_scores(self) -> None:
        for child in self.scores_container.children:
            destroy(child)

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
                else:
                    print(
                        "Error: The highscores file must be"
                        " a JSON list of dictionaries."
                    )

        except FileNotFoundError:
            print(
                f"Info: '{self.gcf.highscore_filename}' not found. "
                "Starting fresh."
            )
        except json.JSONDecodeError as e:
            print(f"Error loading scores: JSON is corrupted ({e})")
        except Exception as e:
            print(f"Unexpected error loading scores: {e}")

        if not highscores:
            Text(
                text="No score added yet",
                origin=(0, 0),
                y=0,
                scale=2,
                color=color.white,
                parent=self.scores_container,
            )
        else:
            y_pos = 0.25
            for i, (name, score) in enumerate(highscores[:10]):
                Text(
                    text=f"{i+1}. {name} - {score} pts",
                    origin=(0, 0),
                    y=y_pos,
                    scale=1.1,
                    color=color.white,
                    parent=self.scores_container,
                )
                y_pos -= 0.06

    def input(self, key: str) -> None:
        if self.enabled and key == "escape":
            self.back_callback()
