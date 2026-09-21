# Ring Pins commercial package

Zero-cash, reversible GameMonetize packaging source for Ring Pins.

The checked-in source is intentionally inactive: `__GAME_ID__` remains unresolved, so the preview build does not load the GameMonetize SDK. This keeps portal activation, external terms, and the game-specific GameId behind the owner approval gate.

## Build preview

```bash
python3 scripts/build_gamemonetize.py --candidate ring-pins
```

## Build activation package after owner approval

```bash
python3 scripts/build_gamemonetize.py --candidate ring-pins --game-id "<GAME_ID>"
```

Commercial signal to watch after activation: completed runs, best-score depth, replay clicks, successful pin depth, and share attempts.

No paid assets, hosting, licenses, subscriptions, contractors, or other cash spend are introduced.
