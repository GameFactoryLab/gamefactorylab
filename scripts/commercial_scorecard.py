#!/usr/bin/env python3
"""Rank Game Factory releases from comparable zero-cost commercial signals.

The script intentionally refuses to declare a winner before there is enough
traffic. It consumes a small JSON file that can be filled from itch.io,
GameMonetize, or other free dashboards without adding an analytics vendor.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_SESSIONS = 25
DECISION_SESSIONS = 50

WEIGHTS = {
    "level3_rate": 0.24,
    "level10_rate": 0.20,
    "replay_rate": 0.20,
    "return_rate": 0.16,
    "share_rate": 0.10,
    "levels_per_session": 0.10,
}

TARGETS = {
    "level3_rate": 0.65,
    "level10_rate": 0.30,
    "replay_rate": 0.15,
    "return_rate": 0.10,
    "share_rate": 0.03,
    "levels_per_session": 4.0,
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
    values = {
        "level3_rate": ratio(game.get("level3_reached"), sessions),
        "level10_rate": ratio(game.get("level10_reached"), sessions),
        "replay_rate": ratio(game.get("replay_sessions"), sessions),
        "return_rate": ratio(game.get("return_sessions"), sessions),
        "share_rate": ratio(game.get("shares"), sessions),
        "levels_per_session": game.get("levels_per_session"),
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

    if sessions < MIN_SESSIONS:
        action = "WAIT_FOR_DATA"
    elif score is None:
        action = "FIX_MEASUREMENT"
    elif sessions >= DECISION_SESSIONS and score < 40:
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
        "commercial_score": None if score is None else round(score, 1),
        "action": action,
    }


def pct(value):
    return "—" if value is None else f"{100*value:.1f}%"


def num(value, digits=1):
    return "—" if value is None else f"{float(value):.{digits}f}"


def render(rows):
    ordered = sorted(
        rows,
        key=lambda r: (
            r["commercial_score"] is not None,
            r["commercial_score"] or -1,
            r.get("sessions", 0),
        ),
        reverse=True,
    )
    lines = [
        "# Game Factory Commercial Scorecard",
        "",
        "This table is a decision aid, not vanity reporting. A game cannot be promoted "
        f"before at least {MIN_SESSIONS} comparable sessions. At {DECISION_SESSIONS}+ "
        "sessions, weak concepts are explicitly eligible to be killed or reworked.",
        "",
        "| Game | Sessions | L3 | L10 | Replay | Return | Share | Lvls/session | Score | Action |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in ordered:
        lines.append(
            f"| {r['name']} | {int(r.get('sessions') or 0)} | "
            f"{pct(r['level3_rate'])} | {pct(r['level10_rate'])} | "
            f"{pct(r['replay_rate'])} | {pct(r['return_rate'])} | "
            f"{pct(r['share_rate'])} | {num(r['levels_per_session'])} | "
            f"{num(r['commercial_score'])} | {r['action']} |"
        )
    lines += [
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
        [{"slug": r["slug"], "score": r["commercial_score"], "action": r["action"]} for r in rows],
        indent=2,
    ))


if __name__ == "__main__":
    main()
