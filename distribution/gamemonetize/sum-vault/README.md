# Sum Vault — GameMonetize candidate

Status: preview-ready, approval-gated.

## Product intent
A longer-session subset-sum puzzle candidate designed for commercial portal testing. The mechanic is deliberately different from Circuit Flow, Orbit Align and the existing reflex, merge, sort, flood, stack, Sudoku and sliding games.

## Included
- 50 deterministic, always-solvable levels.
- Difficulty scales from 6 tiles / 2 seeded solution tiles to 12 tiles / 5 seeded solution tiles.
- Any exact combination is accepted, so players can discover alternate solutions.
- Three lives per attempt.
- Saved unlocked level / last level / best session score.
- Optional hint with score penalty.
- Generated Web Audio effects; no paid or external art/audio assets.
- 3-step game-start loading state.
- GameMonetize GameId placeholder `__GAME_ID__`.
- `SDK_GAME_PAUSE` / `SDK_GAME_START` gameplay gating and audio suspend/resume.
- Ad calls only from explicit Play and selected between-level breaks; never on page load.
- Lightweight local event counters for play, tile toggles, hints, clears, failures and ad-break triggers.

## Approval gate
Do not replace `__GAME_ID__`, upload, verify, request activation, or accept portal terms without owner approval. `scripts/build_gamemonetize.py` remains the only path to create an activation-ready ZIP after a real per-game GameId exists.

Cash spent: €0.
