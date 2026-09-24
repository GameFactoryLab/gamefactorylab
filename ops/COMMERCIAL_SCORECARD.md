# Game Factory Commercial Scorecard

This table is a decision aid, not vanity reporting. The active commercial Top 5 stays at the top. A game cannot be promoted before at least 25 comparable sessions; hard kill/rework decisions start at 100+ sessions unless a portal makes an earlier launch decision.

Primary portal gate: average playtime >= 4:00 when that metric is available.

| Pri | Game | Status | Sessions | Avg time | Gate | Complete | Replay* | Return | Share | Depth/session | Score | Action |
|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Lock Line | active-top5 | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| 2 | Catch Drop | active-top5 | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| 3 | Pattern Relay | active-top5 | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| 4 | Mirror Mark | active-top5 | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| 5 | Ring Pins | active-top5 | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Balance Drop | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Bridge Snap | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Cipher Sprint | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Circuit Flow | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Cluster Collapse | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Gravity Flip | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Orbit Align | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Pixel Logic | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Pulse Cascade | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Route Once | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Rule Shift | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Sum Vault | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |
| — | Vector Drift | release-backlog | 0 | — | — | — | — | — | — | — | — | WAIT_FOR_DATA |

*Replay uses `qualified_replay_sessions` when available: a voluntary replay that reaches the candidate's completed-run threshold. It falls back to `replay_sessions` for older portal data.

## Operating rules

- **PROMOTE**: give the game the next distribution slot and iteration capacity.
- **KEEP_TESTING**: keep live, collect more comparable traffic, make only cheap fixes.
- **LIMIT_EXTRA_WORK**: do not add content yet; improve the core loop only if the fix is cheap.
- **KILL_OR_REWORK**: stop adding content; reuse the shell/mechanic parts elsewhere or run one sharply defined variant.
- **WAIT_FOR_DATA**: no winner claim yet. Distribution is the next job, not more development.
- **FIX_MEASUREMENT**: enough traffic exists but the required comparable signals are missing.

Targets are deliberately simple and editable in `scripts/commercial_scorecard.py`. They are internal decision thresholds, not claims about industry benchmarks.
