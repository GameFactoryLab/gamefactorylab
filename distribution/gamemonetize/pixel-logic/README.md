# Pixel Logic — GameMonetize candidate

Status: preview-ready, approval-gated.

## Product intent
A longer-session row-and-column picture puzzle candidate designed for commercial portal testing. The mechanic is deliberately different from Circuit Flow, Orbit Align, Sum Vault, and the existing reflex, merge, sort, flood, stack, Sudoku, sliding and word-scramble games.

## Included
- 40 deterministic clue puzzles scaling from 5×5 to 8×8.
- Puzzle acceptance is clue-based, so any valid fill satisfying every row and column is accepted.
- Three lives per level; only an explicit wrong **Check puzzle** attempt costs a life.
- Fill and X-mark modes optimized for touch and mouse.
- Saved unlocked level / last level / best session score.
- Optional hint that corrects one unresolved cell with a score penalty.
- Generated Web Audio effects; no paid or external art/audio assets.
- 3-step game-start loading state.
- GameMonetize GameId placeholder `__GAME_ID__`.
- `SDK_GAME_PAUSE` / `SDK_GAME_START` gameplay gating and audio suspend/resume.
- Ad calls only from explicit Play and selected between-level breaks; never on page load.
- Lightweight local event counters for play, cell toggles, mode toggles, hints, checks, clears, failures and ad-break triggers.

## Approval gate
Do not replace `__GAME_ID__`, upload, verify, request activation, or accept portal terms without owner approval. `scripts/build_gamemonetize.py` remains the only path to create an activation-ready ZIP after a real per-game GameId exists.

Cash spent: €0.
