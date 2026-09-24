# Commercial winner selection

Purpose: identify winners faster without buying analytics, ads, hosting, assets, or subscriptions.

## Zero-cash operating loop

1. Ship mechanically distinct games through the free distribution pipeline.
2. Keep the active commercial Top 5 aligned with the current external-distribution queue in `commercial_signals.json`.
3. Enter only observed, comparable signals from free portal dashboards and controlled duel tests.
4. Run `python scripts/commercial_scorecard.py`.
5. Use `COMMERCIAL_SCORECARD.md` to decide where the next development and distribution hour goes.
6. Promote strong signals, keep cheap experiments running, and stop adding content to weak concepts.

The scorecard deliberately blocks premature winner claims. Fewer than 25 comparable sessions means `WAIT_FOR_DATA`. Hard `KILL_OR_REWORK` decisions start at 100+ comparable sessions unless a portal makes an earlier launch decision.

## Signal definitions

- `sessions`: comparable play sessions for the same distribution window.
- `avg_playtime_seconds`: average playtime from the same portal/window when available. The current primary portal gate is 240 seconds.
- `completed_sessions`: sessions that reach the candidate's defined completed-run threshold.
- `qualified_replay_sessions`: sessions where the player voluntarily starts another run and completes the candidate's replay threshold. Use this instead of raw replay clicks when available.
- `replay_sessions`: fallback replay/restart signal for older portal data.
- `return_sessions`: sessions from a player who has previously played the game, when the source exposes it reliably.
- `shares`: successful share actions or copied challenge/share results.
- `depth_per_session`: mechanic-neutral average depth, such as completed runs/rounds per session. Measure it consistently inside each comparison set.
- `priority`: 1–5 only for the current external-distribution Top 5.
- `status`: `active-top5` for the current commercial queue; `release-backlog` for packaged candidates that should not consume scarce distribution/iteration time yet.

Use `null` when a metric is not available. Do not estimate missing data and do not combine incomparable portal windows.

## Decision discipline

The score weights current commercial signals in this order: average playtime, completed-run rate, qualified replay, return behavior, sharing, and session depth. Missing metrics are excluded rather than treated as zero.

The numerical targets are internal operating thresholds, not external industry benchmarks. They exist to enforce consistent decisions across Game Factory candidates. Change them only when live portfolio evidence justifies doing so.

No portal terms, paid service, ad buy, subscription, contractor, license, or irreversible account action is authorized by this system.
