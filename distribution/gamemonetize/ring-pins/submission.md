# Ring Pins — GameMonetize submission handoff

## Portal metadata

- **Title:** Ring Pins
- **Category:** Arcade / Casual
- **Mobile ready:** Yes
- **Controls:** Tap/click or Space/Enter
- **Recommended embed size:** 480 × 720 (responsive)
- **Orientation:** Portrait-friendly; responsive on desktop
- **Language:** English UI; gameplay is language-light
- **Account required:** No
- **External paid assets/services:** None

## Short description

Launch pins into a spinning ring without hitting any pin already attached. The ring accelerates as the score rises and reverses direction every eight successful placements.

## Full description

Ring Pins is a fast one-tap timing arcade game built around instant replay. Tap or click to launch a pin into the spinning ring, avoid every pin already attached, and keep the streak alive as speed increases. Every eight successful pins the ring reverses direction, forcing the player to re-time the next launch. Best score is stored locally so every run has a clear target to beat.

## Instructions

Tap, click, or press Space/Enter to launch a pin. Do not hit an existing pin. Keep placing pins to raise the score. The ring becomes faster and reverses direction every eight points.

## Monetization integration state

This source deliberately contains the placeholder `__GAME_ID__`. The preview package does **not** activate GameMonetize or load its SDK. After the owner creates the game in the GameMonetize dashboard and supplies that game's unique GameId, run:

```bash
python3 scripts/build_gamemonetize.py --candidate ring-pins --game-id "<GAME_ID>"
```

The resulting activation ZIP inserts the GameId and loads the current GameMonetize HTML5 SDK only when the placeholder has been replaced. Ads are requested at the Play boundary and then at a natural result break after every third completed run. Gameplay pauses during `SDK_GAME_PAUSE` and resumes on `SDK_GAME_START`.

Building or storing this handoff does not accept portal terms, request activation, publish the game, or spend cash.
