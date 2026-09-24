# Track Three — release candidate

Working title only; this file does not make a trademark claim.

## Mechanic

A fast visual-tracking game built around three moving cards. At the start of each round one card briefly reveals the target marker, then all three cards become identical and swap positions several times. The player must tap the final position of the target. Correct answers increase the streak and make the next round faster with more swaps; misses cost one of three lives.

## Zero-cash release status

- Self-contained HTML5: one `index.html`, no external runtime assets, paid services or account backend.
- Automatically included by `scripts/build_release_candidates.py` in the zero-cash release-candidate ZIP output.
- Public discovery uses the existing GitHub Pages surface; no paid hosting, ads, assets, licenses or subscriptions are required.
- Score challenges use a normal `?score=` URL and Web Share / clipboard fallback.
- Local-only best score and lightweight local metrics keep initial testing dependency-free.
- Touch, mouse and keyboard controls are supported.

## Signals to watch

Primary: completed run → immediate replay rate.

Secondary: rounds solved per run, longest streak, challenge/share use and challenge opens. Compare only after reasonably comparable free exposure; do not infer a winner from page opens alone.

## Kill / invest gate

Freeze the concept if initial free-distribution replay and session-depth signals remain materially weaker than the strongest active candidates. Give it extra portal media, polish or iteration only if it separates positively on replay, depth, sharing or return behavior.

Cash spend: EUR 0.
