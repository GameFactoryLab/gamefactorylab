# Tunnel Trace — release candidate

Working title only. No trademark claim is made.

## Mechanic

A moving dot approaches an opaque tunnel. The visible approach reveals its direction and speed. Inside the tunnel the dot keeps moving at constant horizontal speed and reflects from the hidden top and bottom walls. The player predicts which of four exit lanes the dot will reach.

This is intentionally different from the active portfolio's timing, catch/dodge, sequence-memory, spatial-transform, visual-tracking and midpoint-estimation mechanics: the core skill is **hidden trajectory extrapolation with reflections**.

## Session design

- 30-second score run.
- ~620 ms visible approach, then an immediate four-lane prediction.
- Vertical speed ramps with completed rounds.
- Correct picks score 100 points plus response-speed and streak bonuses.
- Immediate path reveal after every prediction.
- Local best, completed-run data, replay tracking and score challenge sharing.
- Touch/mouse friendly and self-contained HTML5.

## Zero-cash instrumentation

Stored locally under `gf_tunnel_trace_v1`:

- `page_opens`
- `starts`
- `completed_runs`
- `correct`
- `wrong`
- `replays`
- `manual_restarts`
- `shares`
- `challenge_opens`
- last completed run: score, rounds, correct picks, max streak and duration

No remote analytics, runtime CDN, paid SDK, advertising dependency or backend is required.

## Investment gate

Treat this as a challenger, not a promoted commercial slot. It should earn further work through comparable free exposure and stronger qualified replay/session-depth/share behavior than the current challengers. Hard rework/kill decisions remain data-led rather than rescue-led.

## Distribution

`release-candidates/tunnel-trace/index.html` is picked up automatically by `scripts/build_release_candidates.py`, which creates a self-contained ZIP and rejects remote runtime assets / blocked monetization placeholders.
