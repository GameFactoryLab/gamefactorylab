# Catch Drop — release candidate

## Concept
One-finger arcade game: move a catcher horizontally, collect falling green orbs, grab occasional gold +3 orbs, and avoid red spikes. Missing an orb is safe; one spike hit ends the run. Difficulty rises automatically through faster falling speed, shorter spawn intervals, and a gradually higher spike rate.

## Why this candidate
- Globally understandable visual rules with almost no language dependency.
- Distinct from the current portfolio: catch/avoid with continuous horizontal control rather than lane switching, memory, number, word, merge, timing-ring, stack, or grid-puzzle play.
- Fast to ship: one self-contained HTML file, no images, fonts, audio, backend, libraries, paid assets, or licenses.
- Reuses the established Game Factory visual language: dark field, high-contrast shapes, compact mobile-first layout, local best score, replay and share loop.

## Minimal package
`index.html` only. Canvas graphics, CSS and JavaScript are inline. No external runtime dependencies. The file can be hosted on GitHub Pages or uploaded directly as a single-file HTML5 game where supported.

## QA gate
1. Start / restart works on iOS Safari, Android Chrome and desktop Chrome/Edge.
2. Drag control follows finger without page scrolling.
3. Left/right keyboard control works on desktop.
4. Catch collision feels fair near catcher edges.
5. Red spike reliably ends the run once only.
6. Best score persists after refresh.
7. Share falls back to copied/manual text if native share is unavailable.
8. On a short mobile viewport, Start and share controls remain visible without requiring awkward scrolling during play.

## Zero-cash distribution order
1. GitHub Pages preview and organic links from GameFactoryLab.
2. itch.io HTML5 page, free-to-play with optional donation support.
3. CrazyGames Basic Launch if accepted; do not spend to acquire traffic.
4. GameMonetize submission if accepted, using only its revenue-share monetization path.
5. Organic clips/GIFs/screenshots made from the game itself; no paid media or licensed asset purchases.

## Monetization path
Phase 0: no ads in the GameFactoryLab build; optional itch.io donations.
Phase 1: if accepted by a portal with built-in monetization, use only portal-provided ad/revenue-share tooling. Natural ad break: after a run ends, never during active catching. A rewarded continue may be tested later only if portal rules allow it and retention data justifies the work.

## Investment gate
Primary metric: **average playtime >= 3:00 after at least 500 plays on a distribution portal**. Below the gate, make only zero-cost bug fixes and stop feature expansion. At or above the gate, it qualifies for one focused polish cycle.

## Revenue-funded reinvestment
Until Game Factory revenue is positive: spend EUR 0. After revenue exists, keep at least 70% of earned net revenue uncommitted and allow at most 30% to fund only proven-winner improvements (UX polish, localization where useful, portal integration, or store/distribution fees). No paid ads, subscriptions, contractors, asset packs, licenses, or app-store fees may be funded from outside Game Factory earnings.
