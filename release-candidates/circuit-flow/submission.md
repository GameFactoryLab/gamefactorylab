# Circuit Flow — zero-cash release metadata

## Title
Circuit Flow

## Short description
Rotate circuit tiles, connect IN to OUT, and clear 30 increasingly difficult logic levels.

## Long description
Circuit Flow is a mobile-friendly logic puzzle about restoring a broken circuit. Rotate each tile to build a continuous powered route from the IN terminal to the OUT terminal. The campaign contains 30 deterministic levels that grow from compact 4×4 boards to denser 7×7 circuits. Players have three lives per attempt, can use a hint at a score penalty, and keep unlocked-level progress locally in the browser.

## Instructions
Tap or click a tile to rotate it. Build a connected route from IN on the left to OUT on the right, then press Check path. An incorrect check costs one life. Use Hint to align one intended-route tile at a score penalty. Clear a level to unlock the next one.

## Controls
- Mouse: click a tile to rotate it.
- Touch: tap a tile to rotate it.
- Buttons: Check path, Hint, Restart, Next level, Replay level, Share result.

## Categories / tags
Puzzle, Logic, Brain, Casual, Mobile, HTML5, Connect, Rotate, Circuit

## Commercial test signals
- start / session
- tile_rotate
- check / wrong_check
- hint
- level_clear
- result_clear / result_fail
- replay_click
- share_attempt / share_success / share_copy

Signals are stored locally only. No external analytics endpoint or paid SDK is used.

## Distribution posture
- Standalone HTML5 candidate.
- No external runtime assets.
- No ad SDK.
- No paid license, subscription, hosting, asset, contractor, or app-store dependency.
- No account terms need to be accepted to build or test this package.
- Suitable for zero-cost portal QA after user-controlled account/terms review where required.

## Status
Release candidate ready for automated zero-cash packaging and QA.
