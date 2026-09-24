#!/usr/bin/env python3
from __future__ import annotations

import csv
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
    VIDEO_SPECS,
    WHITE,
    center_text,
    font,
    rounded_panel,
    verify_file,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "handoff" / "fresh-portal-assets"
SLUG = "track-three"
TITLE = "Track Three"
SIGNAL = "completed runs, immediate replay rate, rounds per run, challenge-share rate"


def state_after_swaps(count: int) -> list[int]:
    order = [0, 1, 2]
    swaps = [(0, 1), (1, 2), (0, 2), (0, 1), (1, 2), (0, 2)]
    for a, b in swaps[: count % (len(swaps) + 1)]:
        order[a], order[b] = order[b], order[a]
    return order


def draw_scene(size: tuple[int, int], t: float, cover: bool = False) -> Image.Image:
    img = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(img)
    w, h = size
    margin = int(min(w, h) * 0.07)
    rounded_panel(draw, (margin, margin, w - margin, h - margin), int(min(w, h) * 0.04))
    center_text(draw, (w / 2, margin * 1.9), "TRACK THREE", font(int(min(w, h) * (0.11 if h <= w else 0.085)), True))
    center_text(draw, (w / 2, h * 0.27), "FOLLOW THE MARKED CARD", font(int(min(w, h) * 0.042), True), fill=MUTED)

    lane_centers = [w * 0.25, w * 0.50, w * 0.75]
    card_w = min(w * 0.19, h * 0.22)
    card_h = min(h * 0.38, w * 0.25)
    y = h * 0.58
    order = [0, 1, 2] if cover else state_after_swaps(int(t / 0.8))
    target_identity = 1

    for lane, identity in enumerate(order):
        cx = lane_centers[lane]
        x0, x1 = cx - card_w / 2, cx + card_w / 2
        y0, y1 = y - card_h / 2, y + card_h / 2
        marked = identity == target_identity and (cover or t < 0.9)
        fill = GOLD if marked else CYAN
        draw.rounded_rectangle((x0, y0, x1, y1), radius=max(10, int(card_w * 0.10)), fill=fill)
        center_text(draw, (cx, y), "●" if marked else "?", font(max(24, int(card_w * 0.34)), True), fill=BG if marked else WHITE)

    if not cover:
        round_no = 1 + int(t / 3.2)
        center_text(draw, (w / 2, h * 0.88), f"ROUND {round_no}  •  3 LIVES", font(int(min(w, h) * 0.035), True), fill=GREEN)
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
    marker = "Track Three extension:"
    if marker not in text:
        text += (
            "\nTrack Three extension:\n"
            "- same zero-cash cover set and silent 15-second previews\n"
            "- visual-tracking artwork generated locally from the mechanic\n"
            "- working title only; packaging does not make a trademark claim\n"
        )
        path.write_text(text, encoding="utf-8")


def main() -> None:
    out = DEFAULT_OUT
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to build Track Three preview videos")
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
