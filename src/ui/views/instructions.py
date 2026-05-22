from typing import Callable

from ursina import Text

from src.ui.views.base import BaseView
from src.config.game_config import GameConfig
from src.utils.views_utils import (
    SCORE_ENTRY_COLOR,
    SCORES_TITLE_COLOR,
    SUBTITLE_COLOR,
    TEXT_COLOR,
    TITLE_COLOR,
    TITLE_OUTLINE,
    make_button,
    make_panel,
    update_menu_highlight,
)


class InstructionsView(BaseView):
    """Static help screen reachable from the main menu, dynamically loaded."""

    def __init__(
        self, back_callback: Callable[[], None], game_config: GameConfig
    ) -> None:
        super().__init__()

        self.back_callback = back_callback

        # --- BACKGROUND PANEL ---
        self.border, self.panel = make_panel(self, 0, 0, 0.9, 0.95)

        # --- TITLE ---
        Text(
            text="INSTRUCTIONS",
            origin=(0, 0),
            y=0.395,
            x=0.003,
            scale=3,
            color=TITLE_OUTLINE,
            z=-0.01,
            parent=self,
        )
        Text(
            text="INSTRUCTIONS",
            origin=(0, 0),
            y=0.4,
            scale=3,
            color=TITLE_COLOR,
            z=-0.02,
            parent=self,
        )

        # --- CONFIG EXTRACTION ---
        # (With safe fallback values)
        lives = game_config.lives
        time_limit = game_config.level_max_time
        pts_pacgum = game_config.points_per_pacgum
        pts_super = game_config.points_per_super_pacgum
        pts_ghost = game_config.points_per_ghost
        print(game_config)

        # --- CONTROLS ---
        Text(
            text="CONTROLS",
            origin=(0, 0),
            y=0.25,
            scale=1.5,
            color=SUBTITLE_COLOR,
            z=-0.01,
            parent=self,
        )
        controls_text = (
            "Arrows / WASD: Move Pac-Man\n" "Space / Esc: Pause game"
        )
        Text(
            text=controls_text,
            origin=(0, 0),
            y=0.18,
            scale=1,
            color=TEXT_COLOR,
            z=-0.01,
            parent=self,
        )

        # --- RULES ---
        Text(
            text="GAME RULES",
            origin=(0, 0),
            y=0.05,
            scale=1.5,
            color=SUBTITLE_COLOR,
            z=-0.01,
            parent=self,
        )
        rules_text = (
            f"Eat all pacgums to advance to the next level!\n"
            f"You have {lives} lives and {time_limit} seconds per level."
            "(by default).\n"
            "Run away from ghosts, unless you eat a Super-Pacgum!"
        )
        Text(
            text=rules_text,
            origin=(0, 0),
            y=-0.03,
            scale=1,
            color=TEXT_COLOR,
            z=-0.01,
            parent=self,
        )

        # --- SCORING ---
        Text(
            text="SCORING",
            origin=(0, 0),
            y=-0.15,
            scale=1.5,
            color=SCORES_TITLE_COLOR,
            z=-0.01,
            parent=self,
        )
        scoring_text = (
            f"Pacgum: {pts_pacgum} pts  |  "
            f"Super-Pacgum: {pts_super} pts  |  "
            f"Ghost: {pts_ghost} pts"
        )
        Text(
            text=scoring_text,
            origin=(0, 0),
            y=-0.22,
            scale=1,
            color=SCORE_ENTRY_COLOR,
            z=-0.01,
            parent=self,
        )

        # --- BACK BUTTON ---
        self.btn_back = make_button(self, "Back", y=-0.4)
        self.btn_back.on_click = self.back_callback

        self.elements = [self.btn_back]
        self.selected_index = 0
        self.update_highlight()

    def update_highlight(self) -> None:
        update_menu_highlight(self.elements, self.selected_index)

    def input(self, key: str) -> None:
        if not self.enabled:
            return

        if key in ("backspace", "escape", "space"):
            self.back_callback()
            return
        self.update_highlight()
