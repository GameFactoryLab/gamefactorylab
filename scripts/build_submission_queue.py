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
FRESH_KIT = ROOT / "handoff" / "fresh-submission-kit"
FRESH_META = FRESH_KIT / "submission-metadata.csv"

FRESH_PRIORITY = [
    "lock-line",
    "catch-drop",
    "pattern-relay",
    "mirror-mark",
]

LEGACY_PRIORITY = [
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

CRAZYGAMES_TAG_REFERENCE_DATE = "2026-09-24"
LEGACY_CRAZYGAMES_TAG_OVERRIDES = {
    "ring-pins": "1 Player, 2D, Casual, One Button, Skill, Mobile, Mouse",
}


def load_legacy_games() -> list[dict]:
    games: dict[str, dict] = {}
    for path in sorted(WAVE_DIR.glob("wave*.json")):
        meta = json.loads(path.read_text(encoding="utf-8"))
        if meta.get("cash_spend_eur") != 0:
            raise RuntimeError(f"Non-zero cash spend in {path}")
        wave = meta.get("wave")
        for game in meta.get("games", []):
            row = dict(game)
            row["wave"] = wave
            row["source"] = "legacy"
            tags = row.get("tags", "")
            if isinstance(tags, list):
                tags = ", ".join(tags)
            row["itch_tags"] = tags
            row["crazygames_tags"] = LEGACY_CRAZYGAMES_TAG_OVERRIDES.get(row["slug"], "")
            row["crazygames_tag_reference_date"] = (
                CRAZYGAMES_TAG_REFERENCE_DATE if row["crazygames_tags"] else ""
            )
            games[row["slug"]] = row

    missing = [slug for slug in LEGACY_PRIORITY if slug not in games]
    if missing:
        raise RuntimeError(f"Missing legacy queue metadata for: {missing}")
    return [games[slug] for slug in LEGACY_PRIORITY]


def load_fresh_games() -> list[dict]:
    if not FRESH_META.exists():
        raise RuntimeError(
            "Fresh submission metadata is missing. Run scripts/build_release_candidates.py "
            "and scripts/build_fresh_submission_kit.py before building the consolidated queue."
        )

    with FRESH_META.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    games: dict[str, dict] = {}
    for row in rows:
        if float(row.get("cash_spend_eur", "-1")) != 0:
            raise RuntimeError(f"Non-zero cash spend in fresh candidate {row.get('slug')}")
        row = dict(row)
        row["wave"] = "fresh"
        row["source"] = "fresh"
        row["itch_tags"] = row.get("itch_tags") or row.get("suggested_tags", "")
        row["tags"] = row["itch_tags"]
        games[row["slug"]] = row

    missing = [slug for slug in FRESH_PRIORITY if slug not in games]
    if missing:
        raise RuntimeError(f"Missing fresh queue metadata for: {missing}")
    return [games[slug] for slug in FRESH_PRIORITY]


def package_sources(game: dict) -> tuple[Path, Path]:
    if game["source"] == "fresh":
        return (
            FRESH_KIT / "itch" / game["itch_package"],
            FRESH_KIT / "crazygames-basic" / game["crazygames_basic_package"],
        )
    return (
        DIST / game["itch_package"],
        DIST / "crazygames-basic" / game["crazygames_basic_package"],
    )


def main() -> None:
    games = load_fresh_games() + load_legacy_games()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "itch").mkdir(parents=True)
    (OUT / "crazygames-basic").mkdir(parents=True)

    rows = []
    for rank, game in enumerate(games, start=1):
        itch_tags = game.get("itch_tags", game.get("tags", ""))
        if isinstance(itch_tags, list):
            itch_tags = ", ".join(itch_tags)
        crazygames_tags = game.get("crazygames_tags", "")
        if isinstance(crazygames_tags, list):
            crazygames_tags = ", ".join(crazygames_tags)
        signal = game.get("signal_to_watch", "")
        if isinstance(signal, list):
            signal = ", ".join(signal)
        rows.append(
            {
                "priority": rank,
                "wave": game["wave"],
                "source": game["source"],
                "slug": game["slug"],
                "title": game["title"],
                "status": "READY",
                "itch_package": game["itch_package"],
                "crazygames_basic_package": game["crazygames_basic_package"],
                "short_description": game.get("short_description", ""),
                "itch_tags": itch_tags,
                "crazygames_tags": crazygames_tags,
                "crazygames_tag_reference_date": game.get("crazygames_tag_reference_date", ""),
                # Backward-compatible generic field for older consumers.
                "tags": itch_tags,
                "signal_to_watch": signal,
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
        "The four active fresh candidates are intentionally first. The strongest previously packaged mechanic, Ring Pins, remains slot five as a control/reference release. Older candidates stay queued behind them until current tests earn or lose distribution capacity.",
        "",
        f"CrazyGames tag fallback lists for the immediate Top 5 were checked against the public CrazyGames tag directory on {CRAZYGAMES_TAG_REFERENCE_DATE}. If the live portal omits a listed tag, skip it rather than inventing a replacement.",
        "",
        "## Immediate Top 5",
        "",
    ]
    for row in rows[:5]:
        md += [
            f"### {row['priority']}. {row['title']}",
            f"- Source: `{row['source']}`",
            f"- itch.io ZIP: `{row['itch_package']}`",
            f"- CrazyGames Basic-safe ZIP: `{row['crazygames_basic_package']}`",
            f"- Short description: {row['short_description']}",
            f"- itch.io tags: {row['itch_tags']}",
            f"- CrazyGames tags: {row['crazygames_tags']}",
            f"- CrazyGames tag check: {row['crazygames_tag_reference_date']}",
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
        f"`submission-queue.csv` contains all {len(rows)} currently packaged candidates in current commercial priority order. Only the immediate Top 5 carry prevalidated CrazyGames tag fallbacks; validate tags for a legacy candidate before promoting it into an upload slot.",
    ]
    (OUT / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    for game in games[:5]:
        itch_src, cg_src = package_sources(game)
        if not itch_src.exists() or not cg_src.exists():
            raise RuntimeError(f"Missing built package for {game['slug']}")
        shutil.copy2(itch_src, OUT / "itch" / itch_src.name)
        shutil.copy2(cg_src, OUT / "crazygames-basic" / cg_src.name)

    print(f"Built current Top 5 submission kit and {len(rows)}-game queue at {OUT}")


if __name__ == "__main__":
    main()
