#!/usr/bin/env python3
"""Rank Game Factory releases from comparable zero-cost commercial signals.

The scorecard is intentionally portal-friendly and mechanic-agnostic. It can be
filled from free portal dashboards plus observed replay/share signals without
adding an analytics vendor. Missing metrics stay missing; the script never
fabricates them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_SESSIONS = 25
DECISION_SESSIONS = 100
PLAYTIME_GATE_SECONDS = 240

WEIGHTS = {
    "avg_playtime_seconds": 0.35,
    "completion_rate": 0.20,
    "qualified_replay_rate": 0.20,
    "return_rate": 0.10,
    "share_rate": 0.10,
    "depth_per_session": 0.05,
}

TARGETS = {
    "avg_playtime_seconds": PLAYTIME_GATE_SECONDS,
    "completion_rate": 0.65,
    "qualified_replay_rate": 0.35,
    "return_rate": 0.10,
    "share_rate": 0.03,
    "depth_per_session": 2.0,
}


def ratio(num, den):
    if num is None or den in (None, 0):
        return None
    return max(0.0, float(num) / float(den))


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def score_metric(name, value):
    if value is None:
        return None
    target = TARGETS[name]
    return 100.0 * clamp(float(value) / target)


def derive(game):
    sessions = int(game.get("sessions") or 0)
    completed = game.get("completed_sessions")
    qualified_replays = game.get("qualified_replay_sessions")
    if qualified_replays is None:
        qualified_replays = game.get("replay_sessions")

    depth = game.get("depth_per_session")
    if depth is None:
        # Backward-compatible fallback for the older level-based scorecard.
        depth = game.get("levels_per_session")

    values = {
        "avg_playtime_seconds": game.get("avg_playtime_seconds"),
        "completion_rate": ratio(completed, sessions),
        "qualified_replay_rate": ratio(qualified_replays, sessions),
        "return_rate": ratio(game.get("return_sessions"), sessions),
        "share_rate": ratio(game.get("shares"), sessions),
        "depth_per_session": depth,
    }

    available = {
        key: score_metric(key, value)
        for key, value in values.items()
        if value is not None
    }
    if not available:
        score = None
    else:
        weight_total = sum(WEIGHTS[k] for k in available)
        score = sum(available[k] * WEIGHTS[k] for k in available) / weight_total

    avg_playtime = values["avg_playtime_seconds"]
    if avg_playtime is None:
        gate = "—"
    elif avg_playtime >= PLAYTIME_GATE_SECONDS:
        gate = "PASS"
    elif sessions >= DECISION_SESSIONS:
        gate = "MISS"
    else:
        gate = "PENDING"

    if sessions < MIN_SESSIONS:
        action = "WAIT_FOR_DATA"
    elif score is None:
        action = "FIX_MEASUREMENT"
    elif sessions >= DECISION_SESSIONS and score < 45:
        action = "KILL_OR_REWORK"
    elif score >= 75:
        action = "PROMOTE"
    elif score >= 55:
        action = "KEEP_TESTING"
    else:
        action = "LIMIT_EXTRA_WORK"

    return {
        **game,
        **values,
        "playtime_gate": gate,
        "commercial_score": None if score is None else round(score, 1),
        "action": action,
    }


def pct(value):
    return "—" if value is None else f"{100*value:.1f}%"


def seconds(value):
    if value is None:
        return "—"
    total = int(round(float(value)))
    return f"{total // 60}:{total % 60:02d}"


def num(value, digits=1):
    return "—" if value is None else f"{float(value):.{digits}f}"


def sort_key(row):
    active = row.get("status") == "active-top5"
    priority = int(row.get("priority") or 999)
    return (
        0 if active else 1,
        priority if active else 999,
        -(row["commercial_score"] if row["commercial_score"] is not None else -1),
        -int(row.get("sessions") or 0),
        row.get("name", ""),
    )


def render(rows):
    ordered = sorted(rows, key=sort_key)
    lines = [
        "# Game Factory Commercial Scorecard",
        "",
        "This table is a decision aid, not vanity reporting. The active commercial Top 5 stays at the top. "
        f"A game cannot be promoted before at least {MIN_SESSIONS} comparable sessions; hard kill/rework decisions "
        f"start at {DECISION_SESSIONS}+ sessions unless a portal makes an earlier launch decision.",
        "",
        f"Primary portal gate: average playtime >= {PLAYTIME_GATE_SECONDS // 60}:00 when that metric is available.",
        "",
        "| Pri | Game | Status | Sessions | Avg time | Gate | Complete | Replay* | Return | Share | Depth/session | Score | Action |",
        "|---:|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in ordered:
        priority = r.get("priority") if r.get("status") == "active-top5" else "—"
        lines.append(
            f"| {priority} | {r['name']} | {r.get('status', 'backlog')} | {int(r.get('sessions') or 0)} | "
            f"{seconds(r['avg_playtime_seconds'])} | {r['playtime_gate']} | "
            f"{pct(r['completion_rate'])} | {pct(r['qualified_replay_rate'])} | "
            f"{pct(r['return_rate'])} | {pct(r['share_rate'])} | "
            f"{num(r['depth_per_session'])} | {num(r['commercial_score'])} | {r['action']} |"
        )
    lines += [
        "",
        "*Replay uses `qualified_replay_sessions` when available: a voluntary replay that reaches the candidate's completed-run threshold. "
        "It falls back to `replay_sessions` for older portal data.",
        "",
        "## Operating rules",
        "",
        "- **PROMOTE**: give the game the next distribution slot and iteration capacity.",
        "- **KEEP_TESTING**: keep live, collect more comparable traffic, make only cheap fixes.",
        "- **LIMIT_EXTRA_WORK**: do not add content yet; improve the core loop only if the fix is cheap.",
        "- **KILL_OR_REWORK**: stop adding content; reuse the shell/mechanic parts elsewhere or run one sharply defined variant.",
        "- **WAIT_FOR_DATA**: no winner claim yet. Distribution is the next job, not more development.",
        "- **FIX_MEASUREMENT**: enough traffic exists but the required comparable signals are missing.",
        "",
        "Targets are deliberately simple and editable in `scripts/commercial_scorecard.py`. "
        "They are internal decision thresholds, not claims about industry benchmarks.",
    ]
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="ops/commercial_signals.json")
    p.add_argument("--output", default="ops/COMMERCIAL_SCORECARD.md")
    args = p.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = [derive(game) for game in payload["games"]]
    Path(args.output).write_text(render(rows), encoding="utf-8")
    print(json.dumps(
        [{
            "slug": r["slug"],
            "priority": r.get("priority"),
            "playtime_gate": r["playtime_gate"],
            "score": r["commercial_score"],
            "action": r["action"],
        } for r in sorted(rows, key=sort_key)],
        indent=2,
    ))


if __name__ == "__main__":
    main()
