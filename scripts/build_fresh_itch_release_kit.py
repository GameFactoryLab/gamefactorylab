#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from build_fresh_portal_assets import (
    BG,
    CYAN,
    GOLD,
    GREEN,
    MUTED,
    WHITE,
    center_text,
    draw_scene as base_draw_scene,
    font,
    rounded_panel,
)
from build_midpoint_rush_portal_assets import draw_scene as draw_midpoint_rush_scene
from build_tunnel_trace_portal_assets import draw_scene as draw_tunnel_trace_scene

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-candidates"
OUT = ROOT / "handoff" / "fresh-itch-release-kit"

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
    {
        "priority": 3,
        "slug": "pattern-relay",
        "title": "Pattern Relay",
        "short_description": "Watch the four-pad sequence, repeat it perfectly, and extend the relay as the pace gets faster.",
        "description": "A fast memory relay for short browser sessions. Watch the four-pad sequence, repeat every step in order, and keep extending the chain while the pace accelerates. Chase a local best or send a score challenge to a friend.",
        "controls": "Tap / click / 1-4 keys",
        "tags": "Memory, Puzzle, Skill, High Score",
        "signal": "completed rounds per run, replay rate, score-challenge share rate",
    },
    {
        "priority": 4,
        "slug": "mirror-mark",
        "title": "Mirror Mark",
        "short_description": "Mirror, flip or rotate the marked cell in your head, then tap the transformed position before time runs out.",
        "description": "A fast spatial-reasoning sprint built for short browser sessions. Read the transform, mentally mirror, flip or rotate the marked position on a 5x5 grid, and tap the answer before the 30-second run expires. Chase a local best or send a score challenge to a friend.",
        "controls": "Tap / click",
        "tags": "Puzzle, Spatial, Brain, Skill, High Score",
        "signal": "completed 30-second runs, immediate replay rate, score-challenge share rate",
    },
    {
        "priority": 5,
        "slug": "track-three",
        "title": "Track Three",
        "short_description": "Follow one marked card through faster swaps, then tap the lane where it finishes before three lives are gone.",
        "description": "A fast visual-tracking challenge for short browser sessions. Memorize the marked card, follow it through an increasing number of swaps, then choose its final lane. Correct answers build score and streak while misses cost one of three lives. Replay immediately or send a score challenge to a friend.",
        "controls": "Tap / click / 1-3 keys",
        "tags": "Visual Tracking, Brain, Skill, High Score",
        "signal": "completed runs, immediate replay rate, rounds per run, challenge-share rate",
    },
    {
        "priority": 6,
        "slug": "midpoint-rush",
        "title": "Midpoint Rush",
        "short_description": "Two points appear. Tap their exact midpoint, reveal your error, and chase a cleaner 30-second score.",
        "description": "A quick spatial-estimation challenge for browser play. Two glowing points appear on the board; tap exactly halfway between them, see the true midpoint and your error immediately, then attack the next pair before the 30-second run expires. Chase a local best or send a score challenge to a friend.",
        "controls": "Tap / click",
        "tags": "Puzzle, Spatial, Precision, Brain, Skill, High Score",
        "signal": "completed 30-second runs, immediate replay rate, guesses per run, score-challenge share rate",
    },
    {
        "priority": 7,
        "slug": "tunnel-trace",
        "title": "Tunnel Trace",
        "short_description": "Watch the approach, predict the hidden wall bounces, and choose which exit lane the dot will reach.",
        "description": "A quick hidden-trajectory prediction game. Watch a dot approach an opaque tunnel, infer its direction and speed, then predict which of four exit lanes it reaches after unseen wall reflections. Each answer reveals the path immediately; chase a higher 30-second score or send a score challenge to a friend.",
        "controls": "Tap / click",
        "tags": "Puzzle, Prediction, Physics, Brain, Skill, High Score",
        "signal": "completed 30-second runs, immediate replay rate, prediction accuracy and streak depth, score-challenge share rate",
    },
]

COVER_SIZE = (630, 500)
SCREENSHOT_SIZE = (1280, 720)
SCREENSHOT_TIMES = (1.4, 4.0, 7.2, 10.6)


def draw_track_three(img: Image.Image, t: float, cover: bool = False) -> None:
    w, h = img.size
    draw = ImageDraw.Draw(img)
    margin = int(min(w, h) * 0.07)
    rounded_panel(draw, (margin, margin, w - margin, h - margin), int(min(w, h) * 0.04))
    center_text(draw, (w / 2, margin * 1.9), "TRACK THREE", font(int(min(w, h) * (0.11 if h <= w else 0.085)), True))
    center_text(draw, (w / 2, h * 0.27), "FOLLOW THE MARKED CARD", font(int(min(w, h) * 0.042), True), fill=MUTED)

    lane_centers = [w * 0.25, w * 0.50, w * 0.75]
    card_w = min(w * 0.19, h * 0.22)
    card_h = min(h * 0.38, w * 0.25)
    y = h * 0.58
    order = [0, 1, 2]
    swaps = [(0, 1), (1, 2), (0, 2), (0, 1), (1, 2), (0, 2)]
    if not cover:
        completed = int(t / 0.8)
        for a, b in swaps[: completed % (len(swaps) + 1)]:
            order[a], order[b] = order[b], order[a]
    target_identity = 1
    for lane, identity in enumerate(order):
        cx = lane_centers[lane]
        x0, x1 = cx - card_w / 2, cx + card_w / 2
        y0, y1 = y - card_h / 2, y + card_h / 2
        marked = identity == target_identity and (cover or t < 0.9)
        fill = GOLD if marked else CYAN
        draw.rounded_rectangle((x0, y0, x1, y1), radius=max(10, int(card_w * 0.10)), fill=fill)
        label = "●" if marked else "?"
        center_text(draw, (cx, y), label, font(max(24, int(card_w * 0.34)), True), fill=BG if marked else WHITE)

    if not cover:
        round_no = 1 + int(t / 3.2)
        center_text(draw, (w / 2, h * 0.88), f"ROUND {round_no}  •  3 LIVES", font(int(min(w, h) * 0.035), True), fill=GREEN)


def draw_scene(slug: str, size: tuple[int, int], t: float, cover: bool = False) -> Image.Image:
    if slug == "track-three":
        img = Image.new("RGB", size, BG)
        draw_track_three(img, t, cover=cover)
        return img
    if slug == "midpoint-rush":
        return draw_midpoint_rush_scene(size, t, cover=cover)
    if slug == "tunnel-trace":
        return draw_tunnel_trace_scene(size, t, cover=cover)
    return base_draw_scene(slug, size, t, cover=cover)


def validate_zip(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
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
        "Zero-cash handoff for Lock Line, Catch Drop, Pattern Relay, Mirror Mark, Track Three, Midpoint Rush and Tunnel Trace. Each folder contains the validated HTML5 ZIP, a 630x500 discovery cover, four 1280x720 screenshots, and copy-ready listing text.",
        "",
        "The builder enforces itch.io HTML5 archive limits that can be checked locally: index.html present, <=1000 files, <=240-character paths, <=500 MB extracted content, <=200 MB per file, and no remote runtime assets. Canonical/Open Graph metadata URLs are allowed because they do not load runtime assets.",
        "",
        "Use the candidates under comparable free traffic. Do not buy traffic. Give additional development time only to a candidate that separates on replay, playtime, sharing, or retention.",
        "",
        "## Handoff order",
        "1. Lock Line",
        "2. Catch Drop",
        "3. Pattern Relay",
        "4. Mirror Mark",
        "5. Track Three",
        "6. Midpoint Rush",
        "7. Tunnel Trace",
        "",
        "Track Three, Midpoint Rush and Tunnel Trace remain working titles only; packaging does not make a trademark claim or authorize an irreversible external commitment.",
        "",
        "Cash spend: EUR 0",
    ]
    (OUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"Built itch.io release kit for {len(rows)} candidates at {OUT}")


if __name__ == "__main__":
    main()
