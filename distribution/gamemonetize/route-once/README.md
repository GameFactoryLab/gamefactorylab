# Route Once — GameMonetize candidate

Status: preview-ready, approval-gated.

## Product intent
A longer-session graph-routing puzzle candidate for commercial portal testing. The mechanic is deliberately different from Circuit Flow, Orbit Align, Sum Vault, Pixel Logic, and the existing reflex, merge, sort, flood, stack, Sudoku, sliding, maze and word-scramble games.

## Included
- 40 deterministic graph puzzles scaling from 6 to 13 nodes.
- Every level is guaranteed solvable because generation first creates a complete one-visit route, then adds decoy links.
- Fixed gold start node; visit every node exactly once using visible links.
- Three lives per level; only reaching a true dead end costs a life and resets the route.
- Unlimited undo/restart controls that preserve lives, plus a hint that computes a still-solvable next move.
- Saved unlocked level / last level / best session score.
- Native result sharing with clipboard fallback.
- Generated Web Audio effects; no paid or external art/audio assets.
- 3-step game-start loading state.
- GameMonetize GameId placeholder `__GAME_ID__`.
- `SDK_GAME_PAUSE` / `SDK_GAME_START` gameplay gating and audio suspend/resume.
- Ad calls only from explicit Play and selected between-level breaks; never on page load.
- Lightweight local event counters for play, node visits, dead routes, dead ends, undo, restart, hints, clears, failures, shares and ad-break triggers.

## Approval gate
Do not replace `__GAME_ID__`, upload, verify, request activation, or accept portal terms without owner approval. `scripts/build_gamemonetize.py` remains the only path to create an activation-ready ZIP after a real per-game GameId exists.

Cash spent: €0.
