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
SLUG = "midpoint-rush"
TITLE = "Midpoint Rush"
SIGNAL = "completed 30-second runs, immediate replay rate, guesses per run, score-challenge share rate"


def draw_point(draw: ImageDraw.ImageDraw, x: float, y: float, radius: int, fill) -> None:
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill, outline=WHITE, width=max(2, radius // 6))
    glow = max(radius + 8, int(radius * 1.7))
    draw.ellipse((x - glow, y - glow, x + glow, y + glow), outline=fill, width=max(2, radius // 7))


def draw_scene(size: tuple[int, int], t: float, cover: bool = False) -> Image.Image:
    img = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(img)
    w, h = size
    unit = min(w, h)
    margin = int(unit * 0.07)
    rounded_panel(draw, (margin, margin, w - margin, h - margin), int(unit * 0.04))

    center_text(draw, (w / 2, margin * 1.9), "MIDPOINT RUSH", font(int(unit * (0.105 if h <= w else 0.082)), True))
    center_text(draw, (w / 2, h * 0.26), "TAP THE TRUE MIDPOINT", font(int(unit * 0.041), True), fill=MUTED)

    left = int(w * 0.14)
    right = int(w * 0.86)
    top = int(h * 0.34)
    bottom = int(h * 0.78)
    draw.rounded_rectangle((left, top, right, bottom), radius=max(14, int(unit * 0.025)), fill=(7, 16, 31), outline=(38, 50, 71), width=max(2, int(unit * 0.003)))

    grid = (148, 163, 184)
    for i in range(1, 8):
        x = left + (right - left) * i / 8
        draw.line((x, top, x, bottom), fill=grid, width=1)
    for i in range(1, 5):
        y = top + (bottom - top) * i / 5
        draw.line((left, y, right, y), fill=grid, width=1)

    if cover:
        ax, ay = left + (right - left) * 0.20, top + (bottom - top) * 0.28
        bx, by = left + (right - left) * 0.79, top + (bottom - top) * 0.70
    else:
        ax = left + (right - left) * (0.20 + 0.08 * math.sin(t * 0.73))
        ay = top + (bottom - top) * (0.30 + 0.12 * math.sin(t * 0.91 + 0.6))
        bx = left + (right - left) * (0.78 + 0.07 * math.sin(t * 0.67 + 1.9))
        by = top + (bottom - top) * (0.68 + 0.12 * math.sin(t * 0.83 + 2.4))

    mx, my = (ax + bx) / 2, (ay + by) / 2
    radius = max(10, int(unit * 0.024))
    draw_point(draw, ax, ay, radius, CYAN)
    draw_point(draw, bx, by, radius, PURPLE)

    if cover:
        q_radius = max(16, int(unit * 0.038))
        draw.ellipse((mx - q_radius, my - q_radius, mx + q_radius, my + q_radius), outline=GOLD, width=max(3, q_radius // 7))
        center_text(draw, (mx, my), "?", font(max(18, int(q_radius * 1.10)), True), fill=GOLD)
    else:
        reveal = (t % 2.4) >= 1.0
        if reveal:
            draw.line((ax, ay, bx, by), fill=(125, 139, 157), width=max(2, int(unit * 0.004)))
            actual_r = max(7, int(unit * 0.014))
            draw.ellipse((mx - actual_r, my - actual_r, mx + actual_r, my + actual_r), fill=WHITE)
            error = unit * (0.020 + 0.018 * abs(math.sin(t * 1.7)))
            angle = t * 1.35
            gx, gy = mx + math.cos(angle) * error, my + math.sin(angle) * error
            guess_r = max(12, int(unit * 0.024))
            draw.ellipse((gx - guess_r, gy - guess_r, gx + guess_r, gy + guess_r), outline=GREEN, width=max(3, int(unit * 0.006)))
            draw.line((gx, gy, mx, my), fill=GREEN, width=max(2, int(unit * 0.003)))
            points = max(90, 99 - int(error / max(1, unit) * 180))
            center_text(draw, (w / 2, h * 0.84), f"{points} POINTS  •  {int(error)} px OFF", font(int(unit * 0.032), True), fill=GREEN)
        else:
            center_text(draw, (w / 2, h * 0.84), "FIND THE CENTER", font(int(unit * 0.034), True), fill=GOLD)

    if not cover:
        score = max(0, int(t * 330))
        seconds = max(0, 30 - int(t))
        center_text(draw, (w / 2, h * 0.90), f"{score} SCORE  •  {seconds}s", font(int(unit * 0.030), True), fill=WHITE)
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
            t = frame / FPS
            cover = t < 0.85
            img = draw_scene(render_size, max(0.0, t - 0.85), cover=cover)
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
    marker = "Midpoint Rush extension:"
    if marker not in text:
        text += (
            "\nMidpoint Rush extension:\n"
            "- same zero-cash cover set and silent 15-second previews\n"
            "- spatial-estimation artwork generated locally from the mechanic\n"
            "- working title only; packaging does not make a trademark claim\n"
        )
        path.write_text(text, encoding="utf-8")


def main() -> None:
    out = DEFAULT_OUT
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to build Midpoint Rush preview videos")
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
