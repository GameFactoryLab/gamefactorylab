#!/usr/bin/env python3
from __future__ import annotations

import csv
import shutil
import zipfile
from pathlib import Path

from PIL import Image

from build_fresh_portal_assets import draw_scene

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-candidates"
OUT = ROOT / "handoff" / "fresh-itch-release-kit"

CANDIDATES = [
    {
        "priority": 1,
        "slug": "lock-line",
        "title": "Lock Line",
        "short_description": "Tap when the moving line crosses the target. Center hits score double as timing gets tighter.",
        "description": "A fast one-input precision game. Stop the moving line inside the target, chase center hits for double points, and survive as the timing window tightens. Built for quick browser sessions on desktop and mobile.",
        "controls": "Tap / click / Space",
        "tags": "Arcade, Skill, Precision, High Score",
        "signal": "average playtime, first-session replay rate, result-share rate",
    },
    {
        "priority": 2,
        "slug": "catch-drop",
        "title": "Catch Drop",
        "short_description": "Move the catcher, collect falling orbs, grab gold bonuses, and avoid spikes as the pace rises.",
        "description": "A compact score-chasing arcade game. Move the catcher, collect falling orbs, grab gold bonuses, avoid spikes, and keep up as the pace rises. Designed for quick browser sessions on desktop and mobile.",
        "controls": "Drag / mouse / Left-Right arrows",
        "tags": "Arcade, Skill, High Score",
        "signal": "average playtime, replay rate, score-share rate",
    },
]

COVER_SIZE = (630, 500)
SCREENSHOT_SIZE = (1280, 720)
SCREENSHOT_TIMES = (1.4, 4.0, 7.2, 10.6)


def validate_zip(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Missing candidate package: {path}")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "index.html" not in names:
            raise RuntimeError(f"index.html missing from {path}")
        html = archive.read("index.html").decode("utf-8")
        if "http://" in html or "https://" in html:
            raise RuntimeError(f"Remote runtime URL found in {path}")
        if len(names) > 1000:
            raise RuntimeError(f"itch.io file-count limit exceeded in {path}")
        for name in names:
            if len(name) > 240:
                raise RuntimeError(f"itch.io path-length limit exceeded in {path}: {name}")
        total_uncompressed = sum(info.file_size for info in archive.infolist())
        if total_uncompressed > 500 * 1024 * 1024:
            raise RuntimeError(f"itch.io extracted-size limit exceeded in {path}")
        if any(info.file_size > 200 * 1024 * 1024 for info in archive.infolist()):
            raise RuntimeError(f"itch.io single-file size limit exceeded in {path}")


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)
    if path.stat().st_size == 0:
        raise RuntimeError(f"Generated empty image: {path}")


def listing_text(item: dict[str, object]) -> str:
    return "\n".join(
        [
            f"Title: {item['title']}",
            f"Short description: {item['short_description']}",
            "Kind of project: HTML",
            "Release status: Released",
            "Pricing: Free / no paid access required",
            "Mobile friendly: Yes",
            "Embed: Click to launch in fullscreen",
            "Fullscreen button: Yes",
            f"Description: {item['description']}",
            f"Controls: {item['controls']}",
            f"Suggested tags: {item['tags']}",
            "Language: English",
            "Cash spend: EUR 0",
            f"Signal to watch: {item['signal']}",
            "",
            "Operator note: upload game.zip, cover.png and all four screenshots. Keep metadata accurate and do not add unrelated discovery tags.",
        ]
    ) + "\n"


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    rows: list[dict[str, object]] = []
    for item in CANDIDATES:
        slug = str(item["slug"])
        game_dir = OUT / slug
        game_dir.mkdir(parents=True)

        src = DIST / f"{slug}.zip"
        validate_zip(src)
        shutil.copy2(src, game_dir / "game.zip")

        save_png(draw_scene(slug, COVER_SIZE, 0.0, cover=True), game_dir / "cover.png")
        for idx, t in enumerate(SCREENSHOT_TIMES, start=1):
            save_png(draw_scene(slug, SCREENSHOT_SIZE, t, cover=False), game_dir / f"screenshot-{idx:02d}.png")

        (game_dir / "listing.txt").write_text(listing_text(item), encoding="utf-8")
        rows.append(
            {
                "priority": item["priority"],
                "slug": slug,
                "title": item["title"],
                "status": "READY",
                "game_zip": f"{slug}/game.zip",
                "cover": f"{slug}/cover.png",
                "screenshots": 4,
                "cash_spend_eur": 0,
                "signal_to_watch": item["signal"],
            }
        )

    with (OUT / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    readme = [
        "# Game Factory fresh itch.io release kit",
        "",
        "Zero-cash handoff for Lock Line and Catch Drop. Each folder contains the validated HTML5 ZIP, a 630x500 discovery cover, four 1280x720 screenshots, and copy-ready listing text.",
        "",
        "The builder enforces itch.io HTML5 archive limits that can be checked locally: index.html present, <=1000 files, <=240-character paths, <=500 MB extracted content, <=200 MB per file, and no remote runtime URLs.",
        "",
        "Use the candidates under comparable free traffic. Do not buy traffic. Give additional development time only to a candidate that separates on replay, playtime, sharing, or retention.",
        "",
        "## Handoff order",
        "1. Lock Line",
        "2. Catch Drop",
        "",
        "Cash spend: EUR 0",
    ]
    (OUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"Built itch.io release kit for {len(rows)} candidates at {OUT}")


if __name__ == "__main__":
    main()
