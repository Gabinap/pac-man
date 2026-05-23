# Acceptance Test Plan

## How to run

```
python3 pac-man.py data/config.json
```

All tests are manual unless noted.

---

## 1. Launch and Configuration

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 1.1 | Run with valid config | Game opens, shows main menu | |
| 1.2 | Run with missing config path | Clean error message, no traceback | |
| 1.3 | Run with invalid JSON | Clean error message, no crash | |
| 1.4 | `data/crash.log` created on crash | File appears with timestamp and stack | |

## 2. Main Menu

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 2.1 | Menu appears on launch | Title, difficulty selector, highscores, Start button visible | |
| 2.2 | Change difficulty with arrow keys | Difficulty cycles Easy → Medium → Hard | |
| 2.3 | Highscores displayed | Top scores from `data/highscores.json` shown | |
| 2.4 | Press Enter / Start | Game begins at level 1 | |
| 2.5 | Press I or Instructions button | Instructions view shown | |
| 2.6 | Press S or Settings button | Settings view shown | |

## 3. Maze and Level Generation

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 3.1 | Level 1 generates with seed 42 | Same maze every run | |
| 3.2 | Subsequent levels have random mazes | Different layout each run | |
| 3.3 | Maze dimensions match config | `width` and `height` match `config.json` entries | |
| 3.4 | No dead-end walls blocking full maze | Player can reach all open cells | |
| 3.5 | Ambiance theme applied | Wall/floor textures match configured ambiance | |

## 4. Player

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 4.1 | Player spawns at maze center | Player appears at (0,0) world = center grid cell | |
| 4.2 | Move in all 4 directions | Player moves; cannot pass through walls | |
| 4.3 | Walk animation plays while moving | Skeleton walk cycle visible | |
| 4.4 | Idle animation plays when stopped | Skeleton idle animation plays | |
| 4.5 | FPS mode toggle (configured key) | Camera enters first-person, player model hidden | |
| 4.6 | Cheat mode + Shift | Player moves at 4× speed | |
| 4.7 | Cheat mode = invincible | Ghost collision does not reduce lives | |

## 5. Pacgums

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 5.1 | Pacgums on every open cell | 3D pacgum model visible at each corridor cell | |
| 5.2 | 4 super-pacgums near corners | Larger pacgum model near each corner | |
| 5.3 | Regular pickup awards points | Score increases by `points_per_pacgum` (default 10) | |
| 5.4 | Super pickup awards points + empower | Score +100, player scales up, ghosts flee | |
| 5.5 | All pacgums collected → next level | `NextLevelView` shown after last pickup | |

## 6. Ghosts

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 6.1 | Ghosts spawn at corners | 4 (or configured count) ghosts appear at maze corners | |
| 6.2 | Ghosts move toward player ring | Ghosts converge toward player position | |
| 6.3 | Ghost collides player (normal) | Player stunned, loses 1 life, teleports to spawn, blinks | |
| 6.4 | Ghost collides player (empowered) | Ghost stunned, teleports to spawn, blinks, score +200 | |
| 6.5 | Ghost flees when EMPOWERED | All ghosts move toward their home corner | |
| 6.6 | Ghost revives after stun delay | Ghost reappears at spawn and resumes after 3 s | |
| 6.7 | Per-model speed difference visible | Crockie visibly faster than Grobbo | |

## 7. HUD

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 7.1 | Score displayed and updates | Score counter increases on pickups and ghost kills | |
| 7.2 | Lives displayed | Heart/life count correct; ∞ on Easy | |
| 7.3 | Timer bar decreases | Timer bar shrinks; reaches 0 → GAME OVER | |
| 7.4 | Empowered bar appears on super pickup | Progress bar shown, drains over 6 s | |
| 7.5 | HUD hidden with `h` | All HUD elements disappear; `h` again shows them | |
| 7.6 | Pacgum / super counter updates | Counters decrement on each pickup | |

## 8. Pause

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 8.1 | Press Space during game | Pause overlay shown; game freezes | |
| 8.2 | Resume button / Space again | Game resumes from exact state | |
| 8.3 | Main menu button in pause | Returns to main menu; score reset | |

## 9. Game Over and Victory

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 9.1 | Lose last life | GAME OVER screen with final score | |
| 9.2 | Timer expires | GAME OVER screen with final score | |
| 9.3 | Complete all 10 levels | SUCCESS screen with final score | |
| 9.4 | Name entry field present | Input field accepts alphanumeric, max 10 chars | |
| 9.5 | Register score with valid name | Confirmation shown; score appears in highscores | |
| 9.6 | Register with empty name | Error: "Please enter a name!" | |
| 9.7 | Replay button | Game restarts at level 1 with score 0 | |
| 9.8 | Main menu button | Returns to main menu | |

## 10. Highscores

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 10.1 | New score saved to `data/highscores.json` | File updated after registration | |
| 10.2 | Scores persist across launches | Scores visible in main menu on next run | |
| 10.3 | Scores ranked by value | Higher scores appear first | |

## 11. Difficulty

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 11.1 | Easy mode | Player has infinite lives; ∞ on HUD | |
| 11.2 | Medium mode | Player has `config.lives` lives (default 3) | |
| 11.3 | Hard mode | Player has 1 life; first ghost hit = game over | |
| 11.4 | Change difficulty in menu mid-session | New difficulty applies immediately to current player | |

## 12. Settings and Audio

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 12.1 | Settings view accessible | Opens from main menu | |
| 12.2 | Volume slider changes music level | Ambient music volume changes in real time | |
| 12.3 | Button click sounds audible | Click sound plays on menu navigation | |
| 12.4 | Ambient music plays during game | Background music starts when level begins | |

## 13. All 10 Levels

| # | Test | Expected | Pass? |
|---|------|----------|-------|
| 13.1 | Level 1: 5×5, 2 ghosts | Small maze, 2 ghosts, random ambiance | |
| 13.2 | Level 4: 11×11, 5 ghosts, forest | Forest theme, 5 ghosts | |
| 13.3 | Level 7: 13×13, 10 ghosts, meme | Meme theme, 10 ghosts | |
| 13.4 | Level 10: 19×19, 16 ghosts, 120 s | Max maze, 16 ghosts, 2-min timer | |
| 13.5 | Level counter increments on HUD | "Level X" shown and correct | |
