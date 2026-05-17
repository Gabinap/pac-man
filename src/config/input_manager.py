from typing import Any
from ursina import color, Entity, camera, mouse, Button

import src.config.constants as C


class InputManager:
    """Gère le tampon des touches pour les cheat codes, les raccourcis de triche

    et les interactions spécifiques aux clics de souris (comme le Screen Shake).
    """

    def __init__(self, engine: Any) -> None:
        # Référence vers l'orchestrateur parent (GameEngine)
        self.engine = engine
        self._key_buffer: str = ""
        self.cheat_mode: bool = False

        # La barre rouge de triche est maintenant isolée ici !
        self._cheat_bar: Entity = Entity(
            parent=camera.ui,
            model="quad",
            color=color.red,
            scale=(2, 0.008),
            position=(0, -0.49, -0.5),
            enabled=False,
        )

    def handle_input(self, key: str) -> None:
        """Méthode principale appelée à chaque événement d'entrée clavier/souris."""
        self._update_cheat_buffer(key)
        self._handle_cheat_keys(key)
        self._handle_menu_mouse_click(key)

    def _update_cheat_buffer(self, key: str) -> None:
        """Enregistre les lettres tapées pour détecter l'activation/désactivation de la triche."""
        if len(key) != 1 or not key.isalpha():
            return

        # On garde uniquement les 6 derniers caractères saisis
        self._key_buffer = (self._key_buffer + key)[-6:]

        if self._key_buffer.endswith("cheat"):
            self.set_cheat_mode(True)
        elif self._key_buffer.endswith("normal"):
            self.set_cheat_mode(False)

    def set_cheat_mode(self, enabled: bool) -> None:
        """Bascule l'état du mode triche et met à jour l'interface graphique."""
        if self.cheat_mode == enabled:
            return

        self.cheat_mode = enabled
        self._cheat_bar.enabled = enabled

        # On synchronise l'état avec le joueur actuel s'il est en vie
        if self.engine.session.player:
            self.engine.session.player.cheat_mode = enabled

    def _handle_cheat_keys(self, key: str) -> None:
        """Exécute les commandes secrètes si le mode triche est actif en jeu."""
        if not self.cheat_mode:
            return

        # On n'autorise la triche que si la partie est active et aucun menu n'est ouvert
        if (
            self.engine.game_state != C.EGameState.RUNNING
            or self.engine.router.current is not None
        ):
            return

        # [Triche 'P'] : Mange toutes les pacgums
        if key == "p" and self.engine.session.pacgum_controller:
            if hasattr(self.engine.session.pacgum_controller, "eat_all"):
                self.engine.session.pacgum_controller.eat_all()

        # [Triche 'O'] : Donne les super-pouvoirs au joueur
        elif key == "o" and self.engine.session.player:
            if hasattr(self.engine.session.player, "empower"):
                self.engine.session.player.empower()

    def _handle_menu_mouse_click(self, key: str) -> None:
        """Déclenche un tremblement d'écran si on clique dans le vide du menu principal."""
        if key != "left mouse down":
            return
        if (
            self.engine.router.current != C.EGameView.MENU
            or self.engine.camera_effects.fps_mode
        ):
            return
        # Si on clique sur un vrai bouton du menu, on ne secoue pas l'écran
        if isinstance(mouse.hovered_entity, Button):
            return

        # Appel de l'effet visuel sur le parent
        if hasattr(self.engine, "_shake_screen"):
            self.engine._shake_screen()
