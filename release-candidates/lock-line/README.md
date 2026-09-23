# Lock Line — release candidate

## Why this candidate

Lock Line is a one-input precision game designed for the fastest possible zero-cash test. The player taps when a moving white line crosses a gold target. A center hit scores double. The target narrows and the line speeds up as the score rises.

It is intentionally language-light, mobile-first, self-contained, and asset-free. It does not repeat the existing sorting, maze, memory, circuit, route, orbit, drop, bridge, merge, or ring-pin mechanics.

## Minimal package

- `index.html` — complete game, responsive UI, local best score, local test counters, keyboard support, Web Share / clipboard fallback.
- No remote assets.
- No frameworks.
- No analytics vendor.
- No paid dependency.
- No account or backend.

## Zero-cost distribution

1. itch.io HTML5 upload: use the candidate ZIP produced by the existing release-candidate workflow.
2. CrazyGames Basic Launch: submit the same self-contained build first without platform ads; only integrate the CrazyGames SDK if the game earns a Full Launch.
3. GameFactoryLab project/demo surface for organic discovery and friend sharing. Keep this surface non-commercial; monetization belongs on approved game portals.

Suggested listing copy:
- Title: Lock Line
- Short description: Tap when the moving line crosses the target. Center hits score double.
- Genre/tags: Arcade, Precision, One Button, High Score, Mobile, HTML5
- Controls: Tap / click / Space

## Monetization path

Do not add monetization before traction.

- itch.io: free / pay-what-you-want support.
- CrazyGames: if Basic Launch metrics qualify it for Full Launch, add the current CrazyGames SDK and use platform-approved ad breaks between completed runs only.
- No paid acquisition. Growth comes from the built-in share challenge, portal discovery, and cross-linking from GameFactoryLab winner surfaces.

## Investment gate

Primary gate: **CrazyGames Basic average playtime >= 4:00 minutes**.

Secondary diagnostic signals:
- first-session replay rate >= 35%
- result-share action >= 3%
- at least 100 organic plays before judging a weak result unless the portal makes an earlier launch decision

If the 4-minute playtime gate is missed, freeze the concept after one no-cost tuning pass. Do not buy traffic to rescue it.

## Earned-revenue reinvestment

- First EUR 25 earned: keep 100% reserved; no spend.
- EUR 25–100 cumulative: up to 20% may fund only proven distribution/account fees or store assets directly tied to the top-performing game.
- Above EUR 100 cumulative: up to 30% of incremental Game Factory revenue may be reinvested into the winner; retain the rest as project cash.
- Never spend ahead of earned Game Factory revenue.
