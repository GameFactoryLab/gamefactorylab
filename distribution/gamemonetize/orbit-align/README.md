# Orbit Align — GameMonetize candidate

Status: preview-ready, approval-gated.

## Product intent
A longer-session puzzle candidate designed for GameMonetize rather than the short microgame portfolio. The mechanic is deliberately different from Circuit Flow and the existing sorting, flood, merge, stacking, Sudoku and reflex games.

## Included
- 40 deterministic, always-solvable levels.
- Difficulty scales from 3 orbits × 5 symbols to 6 orbits × 8 symbols.
- Three lives per attempt.
- Saved unlocked level / last level / best session score.
- Optional hint with score penalty.
- Generated Web Audio effects; no paid or external art/audio assets.
- 3-second game-start loading state.
- GameMonetize GameId placeholder `__GAME_ID__`.
- `SDK_GAME_PAUSE` / `SDK_GAME_START` gameplay gating and audio suspend/resume.
- Ad calls only from Play and selected between-level breaks; never on page load.
- Lightweight local event counters for play, move, hint, clear, fail, restart and ad-break triggers.

## Approval gate
Do not replace `__GAME_ID__`, upload, verify, request activation, or accept portal terms without owner approval. `scripts/build_gamemonetize.py` should remain the only path used to create an activation-ready ZIP after a real per-game GameId exists.

Cash spent: €0.
