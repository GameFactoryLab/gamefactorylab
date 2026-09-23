# Pattern Relay — zero-cash release candidate

Status: distribution-ready candidate pending traffic testing. Working title only; no trademark claim or irreversible naming decision is being made.

## Core loop

Watch a four-pad sequence, repeat it exactly, then continue as the sequence grows by one step and the display pace tightens. A single mistake ends the run. The design is one-finger, touch-first, keyboard-compatible, language-light, and built for fast replay.

## Why this candidate exists

Pattern Relay tests a different retention axis from the current Lock Line vs Catch Drop duel: short-term memory progression instead of precision timing or catch-and-avoid reflexes. It stays isolated from the live Fresh Duel until the current two-game comparison has enough signal, so production can increase portfolio optionality without contaminating the active experiment.

## Zero-cash / runtime constraints

- single self-contained HTML5 file
- no remote runtime assets
- no paid SDKs, hosting, analytics, fonts, music, art, licenses, subscriptions, ads, contractors, or backend
- localStorage only for best score and lightweight local counters
- no account or install required
- share uses the browser Web Share API when available, with clipboard fallback
- score-challenge links contain only a numeric score target

## Controls

Touch / mouse: tap pads 1–4 in the displayed order.

Keyboard: keys 1–4. Enter or Space starts a new run after game over.

## Distribution metadata

Category: Puzzle / Memory / Casual

Short description: Watch the sequence, repeat it, and keep the relay alive as each round adds another step and speeds up.

Long description: Pattern Relay is a fast browser memory challenge built around one simple loop: watch four pads flash, repeat the sequence exactly, then face a longer and faster relay. One mistake ends the run, so every extra round becomes a clean reason to replay. No account or install required.

Suggested tags: memory, pattern, puzzle, casual, reaction, score, mobile, html5

Save behavior: local best score only; persistent progress is not required.

## Signal gate

Do not spend extra development time on this mechanic unless distribution data shows stronger replay, average session depth, score-challenge use, or return behavior than weaker portfolio candidates. Kill or freeze it quickly if it does not separate.

## Commercial gate

Cash spend remains EUR 0. Any future paid distribution, licensing, store fee, contractor work, subscription, or monetization integration must be funded by realized Game Factory revenue and separately approved when legally or commercially sensitive.
