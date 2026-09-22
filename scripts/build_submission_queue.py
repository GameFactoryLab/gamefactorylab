#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "handoff" / "top5-submission-kit"
WAVE_DIR = ROOT / "distribution" / "itch"

PRIORITY = [
    "ring-pins",
    "circuit-flow",
    "gravity-flip",
    "bridge-snap",
    "cluster-collapse",
    "pulse-cascade",
    "balance-drop",
    "cipher-sprint",
    "rule-shift",
    "vector-drift",
    "orbit-align",
    "sum-vault",
    "pixel-logic",
    "route-once",
]


def load_games() -> list[dict]:
    games: dict[str, dict] = {}
    for path in sorted(WAVE_DIR.glob("wave*.json")):
        meta = json.loads(path.read_text(encoding="utf-8"))
        if meta.get("cash_spend_eur") != 0:
            raise RuntimeError(f"Non-zero cash spend in {path}")
        wave = meta.get("wave")
        for game in meta.get("games", []):
            row = dict(game)
            row["wave"] = wave
            games[row["slug"]] = row

    missing = [slug for slug in PRIORITY if slug not in games]
    if missing:
        raise RuntimeError(f"Missing queue metadata for: {missing}")
    return [games[slug] for slug in PRIORITY]


def main() -> None:
    games = load_games()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "itch").mkdir(parents=True)
    (OUT / "crazygames-basic").mkdir(parents=True)

    rows = []
    for rank, game in enumerate(games, start=1):
        rows.append(
            {
                "priority": rank,
                "wave": game["wave"],
                "slug": game["slug"],
                "title": game["title"],
                "status": "READY",
                "itch_package": game["itch_package"],
                "crazygames_basic_package": game["crazygames_basic_package"],
                "short_description": game.get("short_description", ""),
                "tags": ", ".join(game.get("tags", [])),
                "signal_to_watch": ", ".join(game.get("signal_to_watch", [])),
            }
        )

    csv_path = OUT / "submission-queue.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    md = [
        "# Game Factory zero-cash submission queue",
        "",
        "Purpose: minimize owner upload friction and get comparable external traffic before more development.",
        "",
        "## Immediate Top 5",
        "",
    ]
    for row in rows[:5]:
        md += [
            f"### {row['priority']}. {row['title']}",
            f"- itch.io ZIP: `{row['itch_package']}`",
            f"- CrazyGames Basic-safe ZIP: `{row['crazygames_basic_package']}`",
            f"- Short description: {row['short_description']}",
            f"- Tags: {row['tags']}",
            f"- Signal to watch: {row['signal_to_watch']}",
            "",
        ]
    md += [
        "## Operating rule",
        "",
        "Publish/test in priority order. Do not add content merely to increase portfolio size. After comparable sessions arrive, promote only mechanics with stronger replay, progression, sharing or traffic signals.",
        "",
        "No paid SDK, paid hosting, paid ads, paid license, paid asset, subscription or contractor is required by this kit.",
        "",
        "`submission-queue.csv` contains all 14 currently packaged candidates in priority order.",
    ]
    (OUT / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for game in games[:5]:
        itch_src = DIST / game["itch_package"]
        cg_src = DIST / "crazygames-basic" / game["crazygames_basic_package"]
        if not itch_src.exists() or not cg_src.exists():
            raise RuntimeError(f"Missing built package for {game['slug']}")
        shutil.copy2(itch_src, OUT / "itch" / itch_src.name)
        shutil.copy2(cg_src, OUT / "crazygames-basic" / cg_src.name)

    print(f"Built Top 5 submission kit and {len(rows)}-game queue at {OUT}")


if __name__ == "__main__":
    main()
