# Ring Pins — Release Candidate

## Goal
Ship one globally understandable, one-tap browser game with no new cash spend and no external assets.

## Core loop
- Tap/click/Space to launch a pin toward a rotating ring.
- A successful pin attaches to the ring and increases score.
- Hitting an existing pin ends the run.
- Rotation speed increases with score and reverses every 8 successful pins.
- Best score persists locally.
- A challenge link can be shared with a target score.

## Build package
Single file: `games/ring-pins/index.html`.

No paid assets, external libraries, fonts, audio, licenses, subscriptions, backend, or store fees are required. The game uses only Canvas, browser storage, Web Share/clipboard APIs, and in-house GameFactory branding.

## QA gate before public promotion
- Mobile portrait: Start, Launch pin, Share score and Show share text remain visible and tappable.
- Desktop: mouse + Space/Enter controls work.
- Restart clears score and collision state.
- Collision reliably ends the run.
- Challenge URL preserves the target score.
- Best score persists after reload.

## Zero-cost distribution
1. GameFactoryLab GitHub Pages direct URL.
2. itch.io HTML5 page (single HTML upload is supported; mark Mobile Friendly after QA).
3. Submit to CrazyGames Basic Launch only after the direct/itch build passes QA. Basic Launch can test a limited audience without requiring the full monetization implementation first.
4. Organic cross-promotion from GameFactoryLab homepage, daily/random rotation and short gameplay clips only after QA.

## Monetization path
- Immediate: itch.io donations are compatible with HTML5 projects; no ad spend required.
- Scale path: if accepted to CrazyGames Full Launch, integrate its HTML5 SDK and use platform ad revenue share. A rewarded continue after one collision is the natural future rewarded-ad placement; an interstitial can sit between completed runs, never mid-run.
- No paid user acquisition until revenue exists.

## Go / no-go metric
Primary investment metric: average playtime >= 4 minutes once the game reaches at least 500 portal plays. This implies multiple replays for a sub-minute core loop and is a better signal than raw clicks.

## Reinvestment rule
- Revenue = 0: spend = 0.
- First earned revenue: keep at least 70% unspent; use at most 30% only on improvements directly tied to the winning title (better cover/creative, analytics/SDK work that remains free where possible, or later store fees only when fully covered by earned Game Factory revenue).
- Expand the mechanic only after the playtime gate is met; otherwise archive the experiment and reuse the code in the next candidate.
