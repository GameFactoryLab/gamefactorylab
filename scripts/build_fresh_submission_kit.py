#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-candidates"
OUT = ROOT / "handoff" / "fresh-submission-kit"

REMOTE_RUNTIME_RE = re.compile(
    r"<(?:script|img|iframe|audio|video|source)\b[^>]*\bsrc\s*=\s*[\"']https?://"
    r"|<object\b[^>]*\bdata\s*=\s*[\"']https?://"
    r"|<link\b(?=[^>]*\brel\s*=\s*[\"'][^\"']*stylesheet[^\"']*[\"'])[^>]*\bhref\s*=\s*[\"']https?://"
    r"|url\(\s*[\"']?https?://",
    re.I,
)
BANNED_MARKERS = (
    "api.gamemonetize.com",
    "googletagmanager.com",
    "google-analytics.com",
    "doubleclick.net",
    "pagead2.googlesyndication.com",
    "__GAME_ID__",
    "__PLACEMENT_ID__",
    "__AD_UNIT__",
)

# Conservative CrazyGames tag vocabulary confirmed against the public CrazyGames
# tags directory on 2026-09-24. Keep this small and explicit so handoff metadata
# fails closed instead of suggesting invented/nonexistent portal tags.
CRAZYGAMES_TAG_REFERENCE_DATE = "2026-09-24"
CRAZYGAMES_PUBLIC_TAGS = {
    "1 Player",
    "2D",
    "Avoid",
    "Brain",
    "Casual",
    "Collect",
    "Logic",
    "Mobile",
    "Mouse",
    "One Button",
    "Skill",
    "Speed",
    "Train your brain",
}

CANDIDATES = [
    {
        "priority": 1,
        "slug": "lock-line",
        "title": "Lock Line",
        "category": "Arcade",
        "short_description": "Tap when the moving line crosses the target. Center hits score double as timing gets tighter.",
        "controls": "Tap / click / Space",
        "progress_save": "No cross-device progress required; local best score only.",
        "itch_tags": "Arcade, Skill, Precision, High Score, Mobile",
        "crazygames_tags": "1 Player, 2D, Casual, One Button, Skill, Speed, Mobile, Mouse",
        "signal_to_watch": "average playtime, first-session replay rate, result-share rate",
    },
    {
        "priority": 2,
        "slug": "catch-drop",
        "title": "Catch Drop",
        "category": "Arcade",
        "short_description": "Move the catcher, collect falling orbs, grab gold bonuses, and avoid spikes as the pace rises.",
        "controls": "Drag / mouse / Left-Right arrows",
        "progress_save": "No cross-device progress required; local best score only.",
        "itch_tags": "Arcade, Skill, Avoid, High Score, Mobile",
        "crazygames_tags": "1 Player, 2D, Avoid, Casual, Collect, Skill, Mobile, Mouse",
        "signal_to_watch": "average playtime, replay rate, score-share rate",
    },
    {
        "priority": 3,
        "slug": "pattern-relay",
        "title": "Pattern Relay",
        "category": "Puzzle",
        "short_description": "Watch the four-pad sequence, repeat it perfectly, and extend the relay as the pace gets faster.",
        "controls": "Tap / click / 1-4 keys",
        "progress_save": "No cross-device progress required; local best score only.",
        "itch_tags": "Memory, Puzzle, Skill, High Score, Mobile",
        "crazygames_tags": "1 Player, 2D, Brain, Casual, Skill, Mobile, Mouse, Train your brain",
        "signal_to_watch": "completed rounds per run, replay rate, score-challenge share rate",
    },
    {
        "priority": 4,
        "slug": "mirror-mark",
        "title": "Mirror Mark",
        "category": "Puzzle",
        "short_description": "Mirror, flip or rotate the marked cell in your head, then tap the transformed position before time runs out.",
        "controls": "Tap / click",
        "progress_save": "No cross-device progress required; local best score only.",
        "itch_tags": "Puzzle, Spatial, Brain, Skill, High Score, Mobile",
        "crazygames_tags": "1 Player, 2D, Brain, Casual, Logic, Skill, Mobile, Mouse, Train your brain",
        "signal_to_watch": "completed 30-second runs, immediate replay rate, score-challenge share rate",
    },
]


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def validate_crazygames_tags(item: dict) -> None:
    tags = split_tags(item["crazygames_tags"])
    if not tags:
        raise RuntimeError(f"No CrazyGames tags configured for {item['slug']}")
    invalid = [tag for tag in tags if tag not in CRAZYGAMES_PUBLIC_TAGS]
    if invalid:
        raise RuntimeError(
            f"Unverified CrazyGames tag(s) for {item['slug']}: {invalid}. "
            f"Use only the public tag allowlist checked {CRAZYGAMES_TAG_REFERENCE_DATE}."
        )


def validate_package(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Missing candidate package: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "index.html" not in names:
            raise RuntimeError(f"index.html missing from {path}")
        html = archive.read("index.html").decode("utf-8")
        if REMOTE_RUNTIME_RE.search(html):
            raise RuntimeError(f"Remote runtime asset found in {path}")
        lower = html.lower()
        for marker in BANNED_MARKERS:
            if marker.lower() in lower:
                raise RuntimeError(f"Blocked runtime/placeholder marker {marker!r} found in {path}")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "itch").mkdir(parents=True)
    (OUT / "crazygames-basic").mkdir(parents=True)

    rows = []
    for item in CANDIDATES:
        validate_crazygames_tags(item)
        src = DIST / f"{item['slug']}.zip"
        validate_package(src)
        itch_name = f"{item['slug']}.zip"
        cg_name = f"{item['slug']}.zip"
        shutil.copy2(src, OUT / "itch" / itch_name)
        shutil.copy2(src, OUT / "crazygames-basic" / cg_name)
        rows.append(
            {
                **item,
                # Backward-compatible generic field for older consumers.
                "suggested_tags": item["itch_tags"],
                "crazygames_tag_reference_date": CRAZYGAMES_TAG_REFERENCE_DATE,
                "status": "READY",
                "itch_package": itch_name,
                "crazygames_basic_package": cg_name,
                "cash_spend_eur": 0,
            }
        )

    with (OUT / "submission-metadata.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    readme = [
        "# Game Factory fresh-candidate submission kit",
        "",
        "Purpose: move the strongest current fresh candidates into external distribution with minimum manual preparation and zero cash spend.",
        "",
        "All candidates are self-contained HTML5 builds with no paid runtime dependencies, remote runtime assets, ads, analytics vendors or account backends. Canonical/Open Graph metadata URLs are permitted because they do not load runtime assets.",
        "",
        f"CrazyGames tag fallback lists were checked against the public CrazyGames tags directory on {CRAZYGAMES_TAG_REFERENCE_DATE}. They are intentionally conservative. If the live submission UI omits a listed tag, skip it instead of inventing a replacement.",
        "",
    ]
    for row in rows:
        readme += [
            f"## {row['priority']}. {row['title']}",
            f"- itch.io upload ZIP: `itch/{row['itch_package']}`",
            f"- CrazyGames Basic-safe ZIP: `crazygames-basic/{row['crazygames_basic_package']}`",
            f"- Category: {row['category']}",
            f"- Short description: {row['short_description']}",
            f"- Controls: {row['controls']}",
            f"- Progress save answer: {row['progress_save']}",
            f"- itch.io tags: {row['itch_tags']}",
            f"- CrazyGames tags: {row['crazygames_tags']}",
            f"- CrazyGames tag check: {row['crazygames_tag_reference_date']}",
            f"- Signal to watch: {row['signal_to_watch']}",
            "",
        ]
    readme += [
        "## Operator rule",
        "",
        "Upload and test candidates under comparable free traffic. Do not buy traffic or add paid services. Give one zero-cost tuning pass only to a candidate that shows stronger replay, average playtime, sharing or portal retention.",
        "",
        "For CrazyGames, use the separately generated fresh portal asset kit for the current required covers and preview videos. The game ZIPs here intentionally contain no SDK or ads and are suitable for Basic-launch testing; monetization work remains gated on traction and platform approval.",
    ]
    (OUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")

    print(f"Built zero-cash fresh submission kit with {len(rows)} candidates at {OUT}")


if __name__ == "__main__":
    main()
