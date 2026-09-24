# Midpoint Rush — release candidate

Working title only; this file does not make a trademark claim.

## Mechanic

Two points appear on a clean playfield. The player taps the exact midpoint between them. The hidden connecting line and true midpoint flash after every guess, showing the error immediately, then a new pair appears. Each 30-second run scores every guess from 0–100 based on normalized distance from the true midpoint; 90+ guesses build a clean streak.

## Why this candidate

This tests a mechanic that is distinct from the current timing, catch/dodge, sequence-memory, spatial-transform, radial-placement and visual-tracking candidates. It is language-light, one-input, instantly restartable, touch/mouse friendly, and uses only generated geometry.

## Zero-cash release status

- Self-contained HTML5: one `index.html`, no external runtime assets, paid services or account backend.
- Automatically included by `scripts/build_release_candidates.py` in the zero-cash release-candidate ZIP output.
- Public discovery can use the existing GitHub Pages surface; no paid hosting, ads, assets, licenses or subscriptions are required.
- Score challenges use a normal `?score=` URL and Web Share / clipboard fallback.
- Local-only best score and lightweight local metrics keep initial testing dependency-free.
- Touch and mouse controls are supported.

## Signals to watch

Primary portal gate: average playtime >= 4:00 when the portal exposes comparable playtime.

Within owned testing, watch completed 30-second runs, immediate replay rate, guesses per run, 90+ accuracy rate, challenge/share use and challenge opens. Compare only after reasonably comparable free exposure.

## Kill / invest gate

Do not add paid traffic or paid polish. Keep the candidate small unless it reaches the portfolio gate (average playtime >= 4:00 where available) or separates positively on qualified replay/depth after at least 100 comparable sessions. One free tuning pass is allowed before freezing a weak result.

Cash spend: EUR 0.
