import random
from typing import Any, Optional
from ursina import destroy, application

import src.config.constants as C
from src.gameplay.maze import Maze
from src.gameplay.entities import Player
from src.gameplay.ghost_controller import GhostController
from src.gameplay.pacgum_controller import PacgumController
from src.utils.timer import Timer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game_engine import GameEngine


class GameSession:
    """Gère les données dynamiques d'une partie en cours, les niveaux et les entités 3D."""

    def __init__(self, engine: "GameEngine") -> None:
        self.engine = engine
        self.score: int = 0
        self.current_level_index: int = 0
        self.is_win: bool = False
        self.game_initialized: bool = False

        # Entités actives du niveau
        self.maze: Optional[Maze] = None
        self.player: Optional[Player] = None
        self.ghost_controller: Optional[GhostController] = None
        self.pacgum_controller: Optional[PacgumController] = None
        self.timer: Optional[Timer] = None

    def init_level(self) -> None:
        """Instancie la géométrie et les entités du niveau actuel."""
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

        # Minuteurs & Labyrinthe
        self.timer = Timer(level_max_time)
        seed = (
            self.engine.config.seed
            if self.current_level_index == 0
            else random.randint(0, 2**31)
        )
        self.maze = Maze(level=level, seed=seed, ambiance=ambiance)

        # Application de la vue caméra
        self.engine.camera_effects.set_topdown()

        # Difficultés & Vies
        if self.engine.difficulty == C.EDifficulty.EASY:
            effective_lives = 0
        elif self.engine.difficulty == C.EDifficulty.HARD:
            effective_lives = 1
        else:
            effective_lives = self.engine.config.lives

        # Création des acteurs autonomes
        self.player = Player(
            self.maze,
            self.engine.config,
            self.engine.game_state,
            lives=effective_lives,
        )
        self.player.cheat_mode = self.engine.input_manager.cheat_mode

        self.ghost_controller = GhostController(
            self.engine,
            self.player,
            self.maze,
            self.engine.game_state,
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
            self.engine.hud.update_level(self.current_level_index + 1)
            self.engine.hud.update_score(self.score)
            self.engine.hud.update_health(self.get_health())

    def on_level_complete(self) -> None:
        """Passage au niveau supérieur ou écran de victoire."""
        if self.timer and self.timer.is_running:
            self.timer.stop()
            self.add_score(self.timer.duration)

        self.current_level_index += 1

        # Condition de victoire générale
        if self.current_level_index >= len(self.engine.config.levels):
            self.is_win = True
            self.engine.game_state = C.EGameState.GAME_OVER
            self.engine.router.switch_view(C.EGameView.GAME_OVER)
            return

        self.destroy_entities()
        self.init_level()
        self.engine.hud.update_level(self.current_level_index)

        if self.timer:
            self.timer.launch_timer()

    def destroy_entities(self) -> None:
        """Nettoie proprement la mémoire avant de changer de niveau ou de quitter."""
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

    def get_health(self) -> int:
        if self.player is None:
            return 0
        if getattr(self.player, "infinite_lives", False) or getattr(
            self.player, "cheat_mode", False
        ):
            return -1
        return self.player.health

    def get_pacgum_count(self) -> int:
        if self.pacgum_controller is None:
            return 0
        return sum(1 for p in self.pacgum_controller.pacgums if not p.is_super)

    def get_super_count(self) -> int:
        if self.pacgum_controller is None:
            return 0
        return sum(1 for p in self.pacgum_controller.pacgums if p.is_super)
