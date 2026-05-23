# Risk Analysis

## Risks Encountered and Mitigated

| Risk | Impact | Probability | Status | Mitigation |
|------|--------|-------------|--------|------------|
| Ursina `Actor` multi-skin GLB crash (Bug 5c) | High | Occurred | Resolved | Patch: attach all `Character` nodes as separate Actors under one Entity |
| Asset file size > GitHub limit (108 MB PNG) | High | Occurred | Resolved | Resized `floor_brick.png` to 1K; downscaled all heavy assets |
| Frame rate below 30 FPS at level load | High | Occurred | Resolved | Removed crashing/heavy models; downscaled assets; lazy-loading via `invoke` |
| Branch divergence (ali / main) | Medium | Recurring | Managed | 3 merge PRs; explicit `game_state` propagation on level 2+ ghost init |
| Ghost stale path after stun (teleport) | Medium | Occurred | Resolved | Set `_ghost_targets[i] = None` when ghost is stunned |
| EASY mode instant game-over (lives = 0) | High | Occurred | Resolved | `lives == 0` → `infinite_lives = True` in Player |
| ANSI escape codes stored in git commit messages | Low | Occurred | Resolved | Python filter-branch script strips `\x1b[...m` before cleanup |
| `src/parser/` deleted without updating import | High | Occurred | Resolved | Import in `pac-man.py` corrected to `src.config.parser` |

## Remaining Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Deployment platform account / build pipeline not set up | High | High | Start packaging script this week; Itch.io free, account creation < 10 min |
| README incomplete at evaluation | High | High | Write README immediately after pm/ is done |
| Ursina version mismatch on evaluator machine | Medium | Low | `uv sync --frozen` locks all deps; `make run` uses the locked venv |
| Ghost AI performance on large mazes (19×19, 16 ghosts) | Medium | Low | BFS is O(V); 361 cells × 16 ghosts is negligible at 60 FPS |
