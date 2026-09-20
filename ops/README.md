# Commercial winner selection

Purpose: identify winners faster without buying analytics, ads, hosting, assets, or subscriptions.

## Zero-cash operating loop

1. Ship mechanically distinct games through the free distribution pipeline.
2. Enter only observed, comparable signals into `commercial_signals.json`.
3. Run `python scripts/commercial_scorecard.py`.
4. Use `COMMERCIAL_SCORECARD.md` to decide where the next development hour goes.
5. Promote strong signals, keep cheap experiments running, and stop adding content to weak concepts.

The scorecard deliberately blocks premature winner claims. Fewer than 25 comparable sessions means `WAIT_FOR_DATA`. At 50+ sessions, a weak score can become `KILL_OR_REWORK`.

## Signal definitions

- `sessions`: comparable play sessions for the same distribution window.
- `level3_reached`: sessions that reached level 3.
- `level10_reached`: sessions that reached level 10.
- `replay_sessions`: sessions containing a replay/restart after a completed or failed run.
- `return_sessions`: sessions from a player who has previously played the game.
- `shares`: successful share actions or copied share results.
- `levels_per_session`: average levels completed/attempted per session, measured consistently across candidates.

Use `null` when a metric is not available. Do not estimate missing data.

## Decision discipline

The numerical targets are internal operating thresholds, not external industry benchmarks. They exist to enforce consistent decisions across Game Factory candidates. Change them only when live portfolio evidence justifies doing so.

No portal terms, paid service, ad buy, subscription, contractor, license, or irreversible account action is authorized by this system.
