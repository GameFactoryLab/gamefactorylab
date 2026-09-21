# Free Distribution Wave 1

Purpose: get external play signals with zero new cash spend and minimal upload friction.

## Priority titles

1. Ring Pins — fastest replay loop / timing signal.
2. Circuit Flow — deeper 30-level session / progression signal.

The canonical submission fields live in `wave1.json`.

## itch.io upload settings

Use the `_itch.zip` package for each game.

- Classification: Game
- Kind of project: HTML
- Release status: Released
- Pricing: Free
- Payments: disabled initially
- Mobile friendly: Yes
- Embed in page: Yes
- Auto-start: No
- Fullscreen button: Yes
- SharedArrayBuffer: No
- Visibility: Draft for smoke test, then Public

Do not add paid assets, paid promotion, external SDKs or subscriptions.

## CrazyGames Basic handoff

Use only the `_crazygames_basic.zip` package. Those builds remove GameFactoryLab cross-promotion so the package is portal-safe before any optional portal SDK or terms decision.

No CrazyGames commercial terms are accepted by this repository workflow.

## Operating decision rule

Do not expand development effort because a game merely ships. Promote a title only after it shows a stronger signal than the current portfolio baseline in at least two of:

- replay / completed run
- share attempt / completed run
- progression depth or score depth
- repeat-session / saved-progress continuation
- external traffic or portal acceptance

Ring Pins and Circuit Flow intentionally test different commercial shapes: a short high-replay arcade loop versus a longer progression puzzle.

Cash spent: €0.
