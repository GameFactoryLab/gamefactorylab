# Dot Glance — zero-cash release candidate

Status: distribution-ready candidate pending traffic testing. Working title only; no trademark claim or irreversible naming decision is being made.

## Core loop

A burst of 3–18 dots appears briefly. The dots disappear and the player chooses the remembered count from three options. Correct answers build a streak and score bonus; mistakes reset the streak and remove 1.2 seconds from the 45-second run. Exposure time tightens gradually as the run deepens.

## Why this candidate exists

Dot Glance tests a distinct perceptual-speed / numerosity mechanic rather than timing, catching, sequence memory, spatial transformation, route logic, sorting or chain reaction. It is intentionally small and self-contained so it can be tested quickly and frozen quickly if replay or sharing is weak.

## Zero-cash / runtime constraints

- single self-contained HTML5 file
- no remote runtime assets
- no paid SDKs, hosting, analytics, fonts, music, art, licenses, subscriptions, ads, contractors or backend
- localStorage only for best score and lightweight local counters
- no account or install required
- score sharing uses Web Share when available with clipboard fallback
- score challenge links contain only a numeric target

## Controls

Touch / mouse: tap one of the three count choices.

Keyboard: keys 1–3 choose the visible answers. Enter or Space starts a run when idle.

## Distribution metadata

Category: Puzzle / Casual / Brain

Short description: Glance at a burst of dots, remember the quantity, and pick the right count before the next flash.

Long description: Dot Glance is a fast visual-counting browser challenge. A field of dots appears for a moment, disappears, and leaves three possible counts. Pick correctly to build a streak while the exposure window gets tighter. Runs last 45 seconds and scores can be sent as friend challenges.

Suggested tags: counting, visual, brain, puzzle, casual, score, mobile, html5

Save behavior: local best score only; cross-device progress is not required.

## Signal gate

Primary: completed run → immediate replay rate.

Secondary: correct-answer rate, rounds completed per run, challenge/share use and return behavior. Compare only after reasonably comparable free exposure; raw page opens alone do not justify investment.

## Kill / invest rule

Freeze the concept after the initial free-distribution test if replay and score-challenge behavior stay materially weaker than the stronger active candidates. Give it portal-specific media or tuning only if it separates positively on replay, session depth, sharing or return play.

Cash spend: EUR 0.
