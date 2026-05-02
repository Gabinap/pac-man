## Dépendances entre modules
 
```
pac-man.py
    │
    ├──► parser.py
    │        │
    │        └──► game_config.py       (retourne un GameConfig)
    │
    └──► visualization.py
             │
             ├──► constants.py
             ├──► entities.py
             └──► game_behavior.py
                      │
                      ├──► constants.py
                      ├──► entities.py
                      └──► game_config.py
```
 
---
 
## Flux de données
 
```
config.json
    │
    ▼
parser.py ──── valide et construit ───► GameConfig
                                            │
                                            ▼
                                     game_behavior.py
                                     ┌───────────────┐
                                     │ - Player       │
                                     │ - Ghost x4     │◄── entities.py
                                     │ - Pacgums      │
                                     │ - Score        │◄── constants.py
                                     │ - Highscores   │
                                     └───────┬────────┘
                                             │ update()
                                             ▼
                                     visualization.py
                                     ┌───────────────┐
                                     │ - Ursina App  │
                                     │ - Camera POV  │
                                     │ - 3D Models   │
                                     │ - Rendu HUD   │
                                     └───────────────┘
```
 
---
 
## Règles d'import
 
| Module | Peut importer | Ne doit PAS importer |
|---|---|---|
| `constants.py` | rien | tout le reste |
| `entities.py` | `constants` | `game_behavior`, `visualization` |
| `game_config.py` | `constants` | `game_behavior`, `visualization` |
| `parser.py` | `game_config`, `constants` | `game_behavior`, `visualization` |
| `game_behavior.py` | `entities`, `game_config`, `constants` | `visualization` |
| `visualization.py` | tout | — |
| `pac-man.py` | `parser`, `visualization` | — |
 