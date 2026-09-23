# Mirror Mark — release candidate

Working title only; this file does not make a trademark claim.

## Mechanic

A 30-second spatial-transform sprint on a 5×5 grid. Each puzzle marks one source cell and asks the player to apply one of three transformations mentally: mirror left/right, flip up/down, or rotate 180 degrees. The player taps the transformed cell. Correct answers build a streak bonus; mistakes reveal the answer and subtract two seconds.

## Zero-cash release status

- Self-contained HTML5: one `index.html`, no external runtime assets or account backend.
- Automatically included by `scripts/build_release_candidates.py` in the zero-cash release-candidate ZIP output.
- Public discovery is intended through the existing GitHub Pages surface; no paid hosting, ads, assets or subscriptions are required.
- Score challenges use a normal `?score=` URL and Web Share/clipboard fallback.
- Local-only best score and lightweight local metrics keep the initial test dependency-free.

## Signals to watch

Primary: completed run → immediate replay rate.

Secondary: correct answers per completed run, score-challenge share use, challenge opens and new-best frequency. Compare only after reasonably comparable free exposure; do not infer a winner from raw page opens alone.

## Kill / invest gate

Freeze the concept after the initial free-distribution test if replay and challenge/share behavior remain materially weaker than the stronger active candidates. Give it additional design or portal-packaging work only if it separates positively on replay, session depth, sharing or return behavior.

Cash spend: EUR 0.
