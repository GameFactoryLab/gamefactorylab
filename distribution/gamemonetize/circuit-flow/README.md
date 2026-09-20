# Circuit Flow — GameMonetize commercial candidate

Status: source-complete, zero-cost, reversible. Do not upload/activate until the owner approves the GameMonetize account terms and provides the per-game GameId.

## Why this exists

Circuit Flow is a longer-form monetization candidate rather than another 30–75 second microgame. It uses a new rotate-the-circuit puzzle mechanic, 30 deterministic levels, saved progression, three lives per attempt, hints, score, touch/mouse controls, and deliberate ad-break hooks.

## GameMonetize integration state

The HTML contains a `__GAME_ID__` placeholder. Replace it with the real GameId created in GameMonetize before packaging. If the placeholder is not replaced, the SDK is not loaded and the game remains an ad-free preview.

The implemented SDK hooks follow the current GameMonetize HTML5 documentation:
- `SDK_GAME_PAUSE` pauses game interaction.
- `SDK_GAME_START` resumes interaction.
- `sdk.showBanner()` is called only after explicit Play and at selected level breaks, never on page load.
- The ZIP root should contain `index.html`.

The game contains no audio, so there is no background audio to mute during ads.

## QA gate before upload

1. Play levels 1, 5, 13, 22, and 30 on desktop.
2. Repeat on a narrow mobile viewport.
3. Confirm wrong Check attempts consume one life and three failures produce retry flow.
4. Confirm Hint aligns one intended path tile and applies a score penalty.
5. Confirm progress/unlocked level persists after reload.
6. Insert the real GameId, open via a local/hosted HTTP origin, and verify SDK state in the GameMonetize dashboard.
7. Confirm ad pause/resume prevents interaction while an ad is active.
8. ZIP with `index.html` at archive root and request activation only after owner approval.

## Commercial signal to watch

Primary: level-3 reach, level-10 reach, return-to-progress rate, average levels per session, and ad impressions per active session once monetization is live.

Kill/iterate rule: if users do not reliably reach level 3 or session depth is weak, simplify the early boards before producing new content. If levels/session and return rate are strong, add visual themes and deeper level patterns using only free/original assets.

Cash spent: €0.
