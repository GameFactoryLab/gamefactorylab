# Pixel Logic — submission draft

## Short description
Use row and column number clues to reveal hidden pixel patterns across a 40-level deterministic logic-puzzle campaign with three lives, hints and saved progress.

## Long description
Pixel Logic is a mobile-first clue-grid puzzle. Each row and column lists the lengths of its filled-cell groups. Players freely fill cells or mark exclusions, then use an explicit Check action when they believe every clue is satisfied. A wrong check costs one of three lives. Hints correct one unresolved cell at a score cost, and campaign progress saves locally.

The campaign scales from 5×5 to 8×8 grids over 40 deterministic levels. Any board state satisfying all row and column clues is accepted, avoiding ambiguity if a clue set admits more than one valid pattern. The game uses generated Web Audio and no paid art, audio, fonts, libraries or external game assets.

## Controls
- Tap/click a cell to apply the active mode.
- Toggle **Mode: Fill / X Mark** to switch between filled cells and exclusions.
- **Check puzzle** validates all row and column clue groups.
- **Hint** corrects one unresolved cell and reduces the level score.

## Monetization placement
- No ad request on page load.
- One ad request after the player explicitly presses Play.
- Optional between-level ad trigger before levels divisible by 5.
- SDK pause/start events suspend and resume gameplay/audio.

## Commercial signals to watch
- level 3 / 10 / 20 / 40 reach
- levels per active session
- wrong checks per clear
- hints per clear
- replay / saved-progress return
- ad impressions per active session after activation

## Approval state
Preview only. `__GAME_ID__` intentionally unresolved. Portal upload, SDK verification, activation request and acceptance of GameMonetize terms require owner approval.

Cash spent: €0.
