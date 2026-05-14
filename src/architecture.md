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
             │        └──► constants.py
             ├──► game_config.py
             ├──► maze.py
             │        ├──► constants.py
             │        ├──► entities.py
             │        └──► game_config.py
             └──► views/
                      ├──► base.py
                      ├──► main_menu.py        ──► base.py
                      ├──► instructions.py     ──► base.py
                      └──► highscores.py       ──► base.py, game_config.py
```

Note : `game_behavior.py` n'est pas encore implémenté (fichier stub avec docstring uniquement). La logique de jeu est actuellement portée par `visualization.GameRender`.

---

## Flux de données

```
config.json
    │
    ▼
parser.py ──── valide et construit ───► GameConfig
                                            │
                                            ▼
                                     visualization.GameRender
                                     ┌──────────────────────┐
                                     │ - Ursina App         │
                                     │ - EGameView (FSM)    │
                                     │ - Camera top-down/FPS│◄── views/*
                                     │ - Barrel distortion  │
                                     │ - Player             │◄── entities.py
                                     │ - Maze (sol + murs)  │◄── maze.py
                                     │ - Ambiance (textures)│◄── constants.py
                                     └──────────────────────┘
```

---

## Règles d'import

| Module | Peut importer | Ne doit PAS importer |
|---|---|---|
| `constants.py` | rien (interne) | tout le reste |
| `game_config.py` | rien (interne) | tout le reste |
| `entities.py` | `constants` | `visualization`, `views`, `maze` |
| `parser.py` | `constants`, `game_config` | `visualization`, `views`, `maze`, `entities` |
| `maze.py` | `constants`, `entities`, `game_config` | `visualization`, `views` |
| `views/base.py` | rien (interne) | tout le reste |
| `views/*.py` | `views/base`, `game_config` | `visualization`, `maze`, `entities` |
| `visualization.py` | tout | — |
| `pac-man.py` | `parser`, `visualization` | — |

---

## Chargement des modèles 3D animés (patches `panda3d-gltf`)

Les assets `.glb` du projet (`assets/models/`) passent par `panda3d-gltf` 1.3.0 quand Ursina les charge via `Actor()`. Cette lib a plusieurs bugs qui empêchent la majorité de nos modèles de s'afficher correctement. Le script [scripts/apply_patches.py](../scripts/apply_patches.py), exécuté automatiquement par `make install`, applique 4 correctifs textuels à [.venv/lib/python3.13/site-packages/gltf/_converter.py](../.venv/lib/python3.13/site-packages/gltf/_converter.py).

### Bug 1 — Plusieurs skins partageant la même racine de squelette

`load_skin` calcule un `root_nodeid` (l'ancêtre commun des joints + mesh) puis stocke `self.skeletons[root_nodeid] = skinid`. Si deux skins ont la même racine, le deuxième écrase le premier et un Character disparaît. Fix : stocker une **liste** de skinids par racine et itérer dessus dans `build_characters`, `add_node`, `build_character`.

### Bug 2 — Accessor sans `bufferView`

Certains GLBs (export Sketchfab/Blender) contiennent des accessors sans champ `bufferView` (par exemple pour des morph targets vides). `sorted(accessors, key=lambda x: x['bufferView'])` lève alors un `KeyError` et le chargement crashe. Fix : filtrer les accessors sans `bufferView` avant le tri.

### Bug 3 — Joints en racines disconnectées

Quand un GLB n'a pas de champ `skin.skeleton` et que ses joints n'ont pas d'ancêtre joint commun (par exemple Crockie qui a 12 joints dont le parent est un non-joint comme `Object_6`), `build_character` tombe dans une branche heuristique qui traite chacun comme racine indépendante sous `<skeleton>`. Fix : injecter `gltf_skin['skeleton'] = root_nodeid` (le LCA déjà calculé par `load_skin`) pour forcer le chemin explicite à une seule récursion couvrant tout l'arbre.

### Bug 4 — Conjugation des translations de joints par `W_mesh`

C'est **le bug principal qui rendait Crockie inutilisable**. Le code original de `combine_mesh_skin` pré-multiplie les vertices par `inverse(W_mesh)` puis laisse le scene graph appliquer `W_mesh` au rendu :

```python
net_xform = NodePath(geom_node.get_parent(0)).get_net_transform()
gvd.transform_vertices(net_xform.get_inverse().get_mat())
```

À la pose bind ça s'annule parfaitement. Mais en animation, le rendu final devient `W_mesh * skin_xform * inverse(W_mesh) * v_meshLocal` : la matrice de skinning est **conjuguée** par `W_mesh`. Pour le scale uniforme, la conjugation préserve les rotations mais **multiplie les translations des joints par le facteur de scale**.

Crockie a une chaîne FBX → GLTF complexe : `fbx (scale=0.01) → Crockie_rig_deform (scale=100) → Object_7 (scale=100) → Object_8 (mesh)`. Cumul : `W_mesh = scale=100`. Toutes les translations d'animation sont donc amplifiées 100×, les vertices baladés très loin, et le mesh apparaît comme une coquille déformée avec faces aplaties.

Grobbo n'a pas le bug parce que sa chaîne est `Sketchfab → mesh` avec `W_mesh = identité`, donc la conjugation est l'identité.

Fix : reparenter directement le `GeomNode` sous le `Character` après le chargement, ce qui retire la chaîne de scale du chemin de rendu. Conforme à la spec GLTF qui stipule que la transform du mesh node ne doit **pas** être appliquée aux vertices skinnés — c'est le skin qui détermine entièrement la position.

```python
NodePath(geom_node).reparent_to(charinfo.nodepath)
```

### Cache modèles Panda3D

Panda3D met en cache les modèles convertis sous forme de `.bam` dans `~/.cache/panda3d/`. À la session suivante, c'est le `.bam` qui est relu — le converter patché n'est jamais invoqué. Tant qu'un cache « pré-patch » subsiste, les modèles restent cassés.

La cible `make patch` vide donc le cache après chaque application via `make clean-model-cache`. Cible accessible manuellement aussi si nécessaire.
