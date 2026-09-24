#!/usr/bin/env python3
from __future__ import annotations

import csv
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from build_fresh_portal_assets import (
    BG,
    COVER_SIZES,
    CYAN,
    DURATION_SECONDS,
    FPS,
    GOLD,
    GREEN,
    MUTED,
    PURPLE,
    VIDEO_SPECS,
    WHITE,
    center_text,
    font,
    rounded_panel,
    verify_file,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "handoff" / "fresh-portal-assets"
SLUG = "tunnel-trace"
TITLE = "Tunnel Trace"
SIGNAL = "completed 30-second runs, immediate replay rate, prediction accuracy and streak depth, score-challenge share rate"


def reflected_y(y0: float, vy: float, t: float, low: float, high: float) -> float:
    span = high - low
    period = span * 2
    z = (y0 - low) + vy * t
    z %= period
    return low + (z if z <= span else period - z)


def path_points(left: float, right: float, low: float, high: float, t: float) -> tuple[list[tuple[float, float]], float]:
    phase = t * 0.55
    y0 = low + (high - low) * (0.34 + 0.16 * math.sin(phase + 0.4))
    vy = (high - low) * (0.58 + 0.14 * math.sin(phase * 1.3 + 1.1))
    if math.sin(phase * 0.8) < 0:
        vy *= -1
    duration = 1.0
    pts: list[tuple[float, float]] = []
    for i in range(81):
        p = i / 80
        x = left + (right - left) * p
        y = reflected_y(y0, vy, p * duration, low, high)
        pts.append((x, y))
    return pts, pts[-1][1]


def draw_scene(size: tuple[int, int], t: float, cover: bool = False) -> Image.Image:
    img = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(img)
    w, h = size
    unit = min(w, h)
    margin = int(unit * 0.07)
    rounded_panel(draw, (margin, margin, w - margin, h - margin), int(unit * 0.04))

    center_text(draw, (w / 2, margin * 1.9), "TUNNEL TRACE", font(int(unit * (0.105 if h <= w else 0.082)), True))
    center_text(draw, (w / 2, h * 0.26), "PREDICT THE HIDDEN EXIT", font(int(unit * 0.041), True), fill=MUTED)

    left = w * 0.16
    entry = w * 0.34
    exit_x = w * 0.82
    low = h * 0.38
    high = h * 0.76
    lane_h = (high - low) / 4

    # Four exit lanes remain visible while the center path is hidden.
    for i in range(4):
        y0 = low + i * lane_h
        fill = (14, 116, 144) if i % 2 == 0 else (99, 102, 241)
        draw.rectangle((exit_x, y0, w * 0.90, y0 + lane_h), fill=tuple(int(c * 0.28) for c in fill), outline=(148, 163, 184), width=max(2, int(unit * 0.003)))
        center_text(draw, ((exit_x + w * 0.90) / 2, y0 + lane_h / 2), str(i + 1), font(max(16, int(unit * 0.030)), True), fill=WHITE)

    pts, exit_y = path_points(left, exit_x, low + unit * 0.02, high - unit * 0.02, t)
    entry_y = min(pts, key=lambda p: abs(p[0] - entry))[1]

    draw.line((left, pts[0][1], entry, entry_y), fill=CYAN, width=max(3, int(unit * 0.006)))
    draw.rounded_rectangle((entry, low, exit_x, high), radius=max(12, int(unit * 0.02)), fill=(8, 18, 34), outline=(71, 85, 105), width=max(3, int(unit * 0.005)))
    center_text(draw, ((entry + exit_x) / 2, (low + high) / 2), "HIDDEN", font(int(unit * 0.045), True), fill=MUTED)

    reveal = cover or (t % 2.6) > 1.05
    if reveal:
        clipped = [(max(entry, x), y) for x, y in pts if x >= entry]
        if len(clipped) >= 2:
            draw.line(clipped, fill=CYAN, width=max(3, int(unit * 0.006)), joint="curve")
        r = max(7, int(unit * 0.014))
        draw.ellipse((exit_x - r, exit_y - r, exit_x + r, exit_y + r), fill=WHITE)
        gate = max(0, min(3, int((exit_y - low) / lane_h)))
        y0 = low + gate * lane_h
        draw.rectangle((exit_x + 3, y0 + 3, w * 0.90 - 3, y0 + lane_h - 3), outline=GREEN, width=max(4, int(unit * 0.007)))
        center_text(draw, (w / 2, h * 0.86), f"EXIT {gate + 1} • PATH REVEALED", font(int(unit * 0.032), True), fill=GREEN)
    else:
        progress = (t % 1.05) / 1.05
        bx = left + (entry - left) * progress
        by = pts[0][1] + (entry_y - pts[0][1]) * progress
        r = max(9, int(unit * 0.018))
        draw.ellipse((bx - r, by - r, bx + r, by + r), fill=GOLD, outline=WHITE, width=max(2, int(unit * 0.003)))
        center_text(draw, (w / 2, h * 0.86), "WATCH SPEED + ANGLE", font(int(unit * 0.032), True), fill=GOLD)

    if not cover:
        score = max(0, int(t * 290))
        seconds = max(0, 30 - int(t))
        center_text(draw, (w / 2, h * 0.91), f"{score} SCORE  •  {seconds}s", font(int(unit * 0.028), True), fill=WHITE)
    return img


def write_cover(size: tuple[int, int], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    draw_scene(size, 0.0, cover=True).save(path, format="PNG", optimize=True)


def encode_preview(render_size: tuple[int, int], output_size: tuple[int, int], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    total_frames = FPS * DURATION_SECONDS
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{render_size[0]}x{render_size[1]}",
        "-r", str(FPS), "-i", "-",
        "-an",
        "-vf", f"scale={output_size[0]}:{output_size[1]}:flags=lanczos",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame in range(total_frames):
            seconds = frame / FPS
            cover = seconds < 0.85
            img = draw_scene(render_size, max(0.0, seconds - 0.85), cover=cover)
            proc.stdin.write(img.tobytes())
    finally:
        proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed for {SLUG}: {path}")


def append_manifest(out: Path) -> None:
    path = out / "asset-manifest.csv"
    if not path.exists():
        raise RuntimeError("Base fresh portal asset manifest is missing; run build_fresh_portal_assets.py first")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows = [row for row in rows if row.get("slug") != SLUG]
    rows.append({
        "slug": SLUG,
        "title": TITLE,
        "landscape_cover": f"{SLUG}/cover-landscape.png",
        "portrait_cover": f"{SLUG}/cover-portrait.png",
        "square_cover": f"{SLUG}/cover-square.png",
        "landscape_preview": f"{SLUG}/preview-landscape.mp4",
        "portrait_preview": f"{SLUG}/preview-portrait.mp4",
        "signal_to_watch": SIGNAL,
        "cash_spend_eur": 0,
    })
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def append_readme(out: Path) -> None:
    path = out / "README.md"
    if not path.exists():
        raise RuntimeError("Base fresh portal README is missing; run build_fresh_portal_assets.py first")
    text = path.read_text(encoding="utf-8")
    marker = "Tunnel Trace extension:"
    if marker not in text:
        text += (
            "\nTunnel Trace extension:\n"
            "- same zero-cash cover set and silent 15-second previews\n"
            "- hidden-trajectory artwork generated locally from the mechanic\n"
            "- working title only; packaging does not make a trademark claim\n"
        )
        path.write_text(text, encoding="utf-8")


def main() -> None:
    out = DEFAULT_OUT
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to build Tunnel Trace preview videos")
    if not out.exists():
        raise RuntimeError("Base fresh portal asset directory is missing; run build_fresh_portal_assets.py first")

    game_dir = out / SLUG
    if game_dir.exists():
        shutil.rmtree(game_dir)
    game_dir.mkdir(parents=True)

    for label, size in COVER_SIZES.items():
        path = game_dir / f"cover-{label}.png"
        write_cover(size, path)
        verify_file(path, max_bytes=5 * 1024 * 1024)

    for label, spec in VIDEO_SPECS.items():
        path = game_dir / f"preview-{label}.mp4"
        encode_preview(spec["render"], spec["output"], path)
        verify_file(path, max_bytes=50 * 1024 * 1024)

    append_manifest(out)
    append_readme(out)
    print(f"Extended fresh portal asset kit with {TITLE} at {game_dir}")


if __name__ == "__main__":
    main()
