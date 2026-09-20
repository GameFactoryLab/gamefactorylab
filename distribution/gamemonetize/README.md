# GameMonetize launch path — PREP ONLY

Status: technically researched and prepared; no account terms accepted and no SDK/GameId activation performed.

## Why this channel matters

GameMonetize currently states a 45% developer revenue share, Net 30 payout, and distribution to its publisher network. There is no upfront publishing fee stated in the developer materials. This makes it compatible with Game Factory's zero-new-cash operating rule once the account/terms are explicitly approved.

Official references:
- https://gamemonetize.com/developers
- https://gamemonetize.com/faq
- https://gamemonetize.com/sdk
- https://github.com/MonetizeGame/GameMonetize.com-SDK

## Technical requirements verified 2026-09-20

1. ZIP root must contain `index.html` and the game files.
2. Each game gets a unique GameId from the developer dashboard.
3. The HTML5 SDK script is initialized with that GameId.
4. Game logic must pause and audio must mute on `SDK_GAME_PAUSE`.
5. Game logic resumes on `SDK_GAME_START` after the ad.
6. Ads are invoked at an appropriate break using `sdk.showBanner()`; do not trigger an ad on initial page load.
7. Upload the game to GameMonetize, verify SDK integration, then request activation.
8. Their current AI-game guidance asks for materially deeper games (at least 10 levels and roughly one hour of content), so the existing 30–75 second microgames should not be the first submissions here.

## Game Factory strategy

Do not submit the entire microgame portfolio to this channel yet. Build/choose a longer-form flagship using the reusable mechanics, then integrate the SDK only after the user approves the account terms and a real GameId exists.

Portal candidate criteria:
- 10+ clearly differentiated levels/stages
- saved progress
- 3 lives or equivalent fail state
- long-session progression rather than a single 30-second run
- ad breaks only after explicit Play / between rounds or levels
- pause/resume-safe timers
- no paid assets or services

## Current blocker

A real GameId requires creating/using a GameMonetize developer account and accepting the platform's terms. Per Game Factory governance, that account/terms step requires explicit user approval. Until then, keep this directory preparation-only.

Cash spent: €0.
