#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "handoff" / "fresh-portal-assets"
FPS = 12
DURATION_SECONDS = 15

BG = (10, 14, 24)
PANEL = (20, 28, 44)
WHITE = (245, 247, 250)
MUTED = (152, 162, 179)
GOLD = (245, 188, 66)
GREEN = (73, 209, 126)
RED = (245, 88, 88)
CYAN = (84, 190, 255)

ASSETS = [
    {
        "slug": "lock-line",
        "title": "LOCK LINE",
        "mechanic": "precision",
        "signal": "average playtime, first-session replay rate, result-share rate",
    },
    {
        "slug": "catch-drop",
        "title": "CATCH DROP",
        "mechanic": "catch",
        "signal": "average playtime, replay rate, score-share rate",
    },
]

COVER_SIZES = {
    "landscape": (1920, 1080),
    "portrait": (800, 1200),
    "square": (800, 800),
}

VIDEO_SPECS = {
    "landscape": {"render": (960, 540), "output": (1920, 1080)},
    "portrait": {"render": (540, 810), "output": (1080, 1620)},
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def center_text(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str, fnt, fill=WHITE) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    w = box[2] - box[0]
    h = box[3] - box[1]
    draw.text((xy[0] - w / 2, xy[1] - h / 2), text, font=fnt, fill=fill)


def rounded_panel(draw: ImageDraw.ImageDraw, box, radius: int) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=PANEL)


def draw_lock_line(img: Image.Image, t: float, cover: bool = False) -> None:
    w, h = img.size
    draw = ImageDraw.Draw(img)
    margin = int(min(w, h) * 0.08)
    rounded_panel(draw, (margin, margin, w - margin, h - margin), int(min(w, h) * 0.04))

    title_size = int(min(w, h) * (0.12 if h <= w else 0.10))
    center_text(draw, (w / 2, margin * 1.9), "LOCK LINE", font(title_size, True))

    track_y = int(h * (0.58 if h <= w else 0.60))
    left = int(w * 0.16)
    right = int(w * 0.84)
    line_h = max(8, int(h * 0.012))
    draw.rounded_rectangle((left, track_y - line_h, right, track_y + line_h), radius=line_h, fill=(55, 65, 82))

    target_center = int(w * (0.58 if cover else (0.48 + 0.18 * math.sin(t * 0.45))))
    target_w = int(w * 0.15)
    if not cover:
        target_w = max(int(w * 0.07), int(w * (0.15 - min(t / 90.0, 0.07))))
    target_h = int(h * 0.11)
    draw.rounded_rectangle(
        (target_center - target_w // 2, track_y - target_h // 2, target_center + target_w // 2, track_y + target_h // 2),
        radius=max(8, target_h // 5),
        fill=GOLD,
    )

    if cover:
        line_x = int(w * 0.38)
    else:
        phase = (t * (0.55 + 0.03 * min(t, 10))) % 2.0
        p = phase if phase <= 1.0 else 2.0 - phase
        line_x = int(left + p * (right - left))
    needle_w = max(5, int(w * 0.008))
    draw.rounded_rectangle((line_x - needle_w, track_y - int(h * 0.16), line_x + needle_w, track_y + int(h * 0.16)), radius=needle_w, fill=WHITE)

    if not cover:
        score = max(0, int(t * 0.75))
        score_text = str(score)
        center_text(draw, (w / 2, h * 0.29), score_text, font(int(min(w, h) * 0.11), True), fill=WHITE)

        pulse = abs(line_x - target_center) < target_w // 2
        if pulse:
            r = int(min(w, h) * (0.05 + 0.02 * math.sin(t * 14)))
            draw.ellipse((target_center - r, track_y - r, target_center + r, track_y + r), outline=WHITE, width=max(3, r // 10))


def draw_spike(draw: ImageDraw.ImageDraw, x: float, y: float, size: float) -> None:
    draw.polygon([(x, y - size), (x - size, y + size), (x + size, y + size)], fill=RED)


def draw_catch_drop(img: Image.Image, t: float, cover: bool = False) -> None:
    w, h = img.size
    draw = ImageDraw.Draw(img)
    margin = int(min(w, h) * 0.07)
    rounded_panel(draw, (margin, margin, w - margin, h - margin), int(min(w, h) * 0.04))

    title_size = int(min(w, h) * (0.12 if h <= w else 0.10))
    center_text(draw, (w / 2, margin * 1.9), "CATCH DROP", font(title_size, True))

    field_top = int(h * 0.25)
    field_bottom = int(h * 0.86)
    catcher_y = int(h * 0.79)
    catcher_w = int(w * 0.22)
    catcher_h = max(14, int(h * 0.035))
    if cover:
        catcher_x = w / 2
    else:
        catcher_x = w * (0.50 + 0.28 * math.sin(t * 0.9))
    draw.rounded_rectangle(
        (catcher_x - catcher_w / 2, catcher_y - catcher_h / 2, catcher_x + catcher_w / 2, catcher_y + catcher_h / 2),
        radius=catcher_h // 2,
        fill=CYAN,
    )

    specs = [
        (0.28, 0.00, GREEN, 1.00),
        (0.52, 0.80, GOLD, 1.10),
        (0.73, 1.70, GREEN, 0.95),
        (0.40, 2.40, RED, 1.05),
        (0.62, 3.10, GREEN, 1.00),
    ]
    orb_r = max(10, int(min(w, h) * 0.035))
    for idx, (xfrac, offset, color, speed) in enumerate(specs):
        if cover:
            yfrac = [0.40, 0.49, 0.36, 0.56, 0.44][idx]
        else:
            cycle = ((t * speed + offset) % 4.8) / 4.8
            yfrac = field_top / h + cycle * ((field_bottom - field_top) / h)
        x = int(w * xfrac)
        y = int(h * yfrac)
        if color == RED:
            draw_spike(draw, x, y, orb_r)
        else:
            draw.ellipse((x - orb_r, y - orb_r, x + orb_r, y + orb_r), fill=color)
            if color == GOLD:
                center_text(draw, (x, y), "+3", font(max(10, orb_r // 2), True), fill=BG)

    if not cover:
        score = max(0, int(t * 1.4))
        center_text(draw, (w / 2, h * 0.20), str(score), font(int(min(w, h) * 0.09), True), fill=WHITE)


def draw_scene(slug: str, size: tuple[int, int], t: float, cover: bool = False) -> Image.Image:
    img = Image.new("RGB", size, BG)
    if slug == "lock-line":
        draw_lock_line(img, t, cover=cover)
    elif slug == "catch-drop":
        draw_catch_drop(img, t, cover=cover)
    else:
        raise ValueError(slug)
    return img


def write_cover(slug: str, size: tuple[int, int], path: Path) -> None:
    img = draw_scene(slug, size, 0.0, cover=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def encode_preview(slug: str, render_size: tuple[int, int], output_size: tuple[int, int], path: Path) -> None:
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
            img = draw_scene(slug, render_size, max(0.0, t - 0.85), cover=cover)
            proc.stdin.write(img.tobytes())
    finally:
        proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed for {slug}: {path}")


def verify_file(path: Path, max_bytes: int | None = None) -> None:
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError(f"Missing generated asset: {path}")
    if max_bytes is not None and path.stat().st_size > max_bytes:
        raise RuntimeError(f"Generated asset exceeds size gate: {path} ({path.stat().st_size} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.out

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to build CrazyGames preview videos")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    rows = []
    for item in ASSETS:
        game_dir = out / item["slug"]
        game_dir.mkdir(parents=True)
        for label, size in COVER_SIZES.items():
            path = game_dir / f"cover-{label}.png"
            write_cover(item["slug"], size, path)
            verify_file(path, max_bytes=5 * 1024 * 1024)

        for label, spec in VIDEO_SPECS.items():
            path = game_dir / f"preview-{label}.mp4"
            encode_preview(item["slug"], spec["render"], spec["output"], path)
            verify_file(path, max_bytes=50 * 1024 * 1024)

        rows.append({
            "slug": item["slug"],
            "title": item["title"].title(),
            "landscape_cover": f"{item['slug']}/cover-landscape.png",
            "portrait_cover": f"{item['slug']}/cover-portrait.png",
            "square_cover": f"{item['slug']}/cover-square.png",
            "landscape_preview": f"{item['slug']}/preview-landscape.mp4",
            "portrait_preview": f"{item['slug']}/preview-portrait.mp4",
            "signal_to_watch": item["signal"],
            "cash_spend_eur": 0,
        })

    with (out / "asset-manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    readme = [
        "# Fresh candidate CrazyGames asset kit",
        "",
        "Zero-cash, original portal media generated from the mechanics and visual language of Lock Line and Catch Drop.",
        "",
        "Per candidate:",
        "- `cover-landscape.png` — 1920×1080",
        "- `cover-portrait.png` — 800×1200",
        "- `cover-square.png` — 800×800",
        "- `preview-landscape.mp4` — 1920×1080, 15 seconds, silent",
        "- `preview-portrait.mp4` — 1080×1620 (2:3), 15 seconds, silent",
        "",
        "The covers contain only the game title plus original mechanic-inspired artwork. Videos open on the matching cover look and then show a deterministic gameplay-style animation with no audio, cursor, store logo, social icon or promotional CTA.",
        "",
        "Operator rule: preview these files before portal upload. Do not accept new paid terms, buy traffic, or integrate monetization for Basic Launch. Deeper work is gated on real playtime/replay/share signals.",
        "",
        "Cash spend: EUR 0.",
    ]
    (out / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(f"Built portal asset kit for {len(ASSETS)} candidates at {out}")


if __name__ == "__main__":
    main()
