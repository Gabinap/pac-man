import random
from typing import TYPE_CHECKING

from ursina import destroy

import src.config.constants as C
from src.gameplay.entities import Player
from src.gameplay.ghost_controller import GhostController
from src.gameplay.maze import Maze
from src.gameplay.pacgum_controller import PacgumController
from src.utils.timer import Timer

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class GameSession:
    """Dynamic state of a running game: levels, score, 3D entities."""

    def __init__(self, engine: "GameEngine") -> None:
        self.engine = engine
        self.score: int = 0
        self.current_level_index: int = 0
        self.is_win: bool = False
        self.game_initialized: bool = False

        self.maze: Maze | None = None
        self.player: Player | None = None
        self.ghost_controller: GhostController | None = None
        self.pacgum_controller: PacgumController | None = None
        self.timer: Timer | None = None

    def timer_over_action(self) -> None:
        self.engine.game_state = C.EGameState.GAME_OVER
        self.engine.router.switch_view(C.EGameView.GAME_OVER)

    def init_level(self) -> None:
        """Build geometry and entities for the current level."""
        level = self.engine.config.levels[self.current_level_index]
        ambiance = (
            C.AMBIANCES[level.ambiance]
            if level.ambiance is not None
            else random.choice(list(C.AMBIANCES.values()))
        )
        ghost_count = (
            level.ghost_count
            if level.ghost_count is not None
            else C.GHOST_COUNT
        )
        level_max_time = (
            level.level_max_time or self.engine.config.level_max_time
        )

        self.timer = Timer(level_max_time, self.timer_over_action)
        seed = (
            self.engine.config.seed
            if self.current_level_index == 0
            else random.randint(0, 2**31)
        )
        self.maze = Maze(level=level, seed=seed, ambiance=ambiance)

        self.engine.camera_effects.set_topdown()

        self.player = Player(
            self.maze,
            self.engine.config,
            self.engine.game_state,
            lives=self.lives_for_current_difficulty(),
            controls=self.engine.controls,
        )
        self.player.cheat_mode = self.engine.input_manager.cheat_mode

        self.ghost_controller = GhostController(
            self.engine,
            self.player,
            self.maze,
            self.engine.game_state,
            self.add_score,
            ghost_count,
        )
        self.pacgum_controller = PacgumController(
            self.engine,
            self.player,
            self.maze,
            ambiance,
            self.engine.config,
        )

        self.game_initialized = True

        if self.engine and self.engine.hud:
            self.engine.hud.update_level(self.current_level_index)
            self.engine.hud.update_score(self.score)
            self.engine.hud.update_health(self.get_health())

    def on_level_complete(self) -> None:
        """Advance to the next level or show the victory screen."""
        if self.timer and self.timer.is_running:
            self.timer.stop()
            self.add_score(self.timer.duration)

        self.current_level_index += 1

        if self.current_level_index >= len(self.engine.config.levels):
            self.is_win = True
            self.engine.game_state = C.EGameState.GAME_OVER
            self.engine.router.switch_view(C.EGameView.GAME_OVER)
            return
        else:
            self.engine.router.switch_view(C.EGameView.NEXT_LEVEL)

    def destroy_entities(self) -> None:
        """Release level-scoped entities before changing level or quitting."""
        if not self.game_initialized:
            return

        if self.timer:
            self.timer.destroy_timer()
        if self.maze:
            destroy(self.maze)
        if self.player:
            destroy(self.player)
        if self.ghost_controller:
            for ghost in self.ghost_controller.ghosts:
                destroy(ghost)
        if self.pacgum_controller:
            self.pacgum_controller.destroy_all()

        self.game_initialized = False

    def add_score(self, points: int) -> None:
        self.score += points
        self.engine.hud.update_score(self.score)

    def lives_for_current_difficulty(self) -> int:
        """Starting lives for the current difficulty.

        EASY → 0 (Player interprets this as infinite_lives), HARD → 1,
        MEDIUM → the configured value (`config.lives`).
        """
        if self.engine.difficulty == C.EDifficulty.EASY:
            return 0
        if self.engine.difficulty == C.EDifficulty.HARD:
            return 1
        return self.engine.config.lives

    def apply_difficulty_to_player(self) -> None:
        """Re-align `player.infinite_lives` and `player.health` to the current
        difficulty and push the result to the HUD.

        Lets the menu change difficulty without recreating the Player (which
        is instantiated once in ``GameEngine.__init__``).
        """
        if self.player is None:
            return
        lives = self.lives_for_current_difficulty()
        self.player.infinite_lives = lives == 0
        self.player.health = lives
        if self.engine.hud:
            self.engine.hud.update_health(self.get_health())

    def get_health(self) -> int:
        if self.player is None:
            return 0
        if getattr(self.player, "infinite_lives", False) or getattr(
            self.player, "cheat_mode", False
        ):
            return -1
        return self.player.health

    def get_level(self) -> int:
        return self.current_level_index + 1

    def get_pacgum_count(self) -> int:
        if self.pacgum_controller is None:
            return 0
        return sum(1 for p in self.pacgum_controller.pacgums if not p.is_super)

    def get_super_count(self) -> int:
        if self.pacgum_controller is None:
            return 0
        return sum(1 for p in self.pacgum_controller.pacgums if p.is_super)
