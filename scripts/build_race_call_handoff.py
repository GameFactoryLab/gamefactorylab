#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist-candidates"
SUBMISSION_OUT = ROOT / "handoff" / "fresh-submission-kit"
ITCH_OUT = ROOT / "handoff" / "fresh-itch-release-kit"
PORTAL_OUT = ROOT / "handoff" / "fresh-portal-assets"
SLUG = "race-call"
TITLE = "Race Call"
SIGNAL = "completed 30-second runs, immediate replay rate, correct predictions and streak/round depth, score-challenge share rate"
CRAZYGAMES_TAG_REFERENCE_DATE = "2026-09-24"

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


def candidate_zip() -> Path:
    path = DIST / f"{SLUG}.zip"
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
    return path


def rewrite_csv(path: Path, row: dict[str, object]) -> None:
    if not path.exists():
        raise RuntimeError(f"Base manifest missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not fieldnames:
        raise RuntimeError(f"Manifest has no header: {path}")
    rows = [item for item in rows if item.get("slug") != SLUG]
    normalized = {name: row.get(name, "") for name in fieldnames}
    rows.append(normalized)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_readme(path: Path, marker: str, text: str) -> None:
    if not path.exists():
        raise RuntimeError(f"Base README missing: {path}")
    current = path.read_text(encoding="utf-8")
    if marker not in current:
        current = current.rstrip() + "\n\n" + text.strip() + "\n"
        path.write_text(current, encoding="utf-8")


def build_submission() -> None:
    src = candidate_zip()
    if not SUBMISSION_OUT.exists():
        raise RuntimeError("Base fresh submission kit is missing; run build_fresh_submission_kit.py first")
    for portal in ("itch", "crazygames-basic"):
        target_dir = SUBMISSION_OUT / portal
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target_dir / f"{SLUG}.zip")

    rewrite_csv(
        SUBMISSION_OUT / "submission-metadata.csv",
        {
            "priority": 9,
            "slug": SLUG,
            "title": TITLE,
            "category": "Skill",
            "short_description": "Compare head starts and speed, then call which racer reaches the finish first before time runs out.",
            "controls": "Tap / click; 1 or Up Arrow = Top, 2 or Down Arrow = Bottom",
            "progress_save": "No cross-device progress required; local best score only.",
            "itch_tags": "Skill, Prediction, High Score, Casual, One Button, Mobile",
            "crazygames_tags": "1 Player, 2D, Brain, Casual, Skill, Speed, Mobile, Mouse",
            "signal_to_watch": SIGNAL,
            "suggested_tags": "Skill, Prediction, High Score, Casual, One Button, Mobile",
            "crazygames_tag_reference_date": CRAZYGAMES_TAG_REFERENCE_DATE,
            "status": "READY",
            "itch_package": f"{SLUG}.zip",
            "crazygames_basic_package": f"{SLUG}.zip",
            "cash_spend_eur": 0,
        },
    )
    append_readme(
        SUBMISSION_OUT / "README.md",
        "Race Call extension:",
        f"""
Race Call extension:
- itch.io upload ZIP: `itch/{SLUG}.zip`
- CrazyGames Basic-safe ZIP: `crazygames-basic/{SLUG}.zip`
- Category: Skill
- Controls: Tap / click; keyboard 1/Up for Top, 2/Down for Bottom
- itch.io tags: Skill, Prediction, High Score, Casual, One Button, Mobile
- CrazyGames tags: 1 Player, 2D, Brain, Casual, Skill, Speed, Mobile, Mouse
- CrazyGames tag check: {CRAZYGAMES_TAG_REFERENCE_DATE}
- Signal to watch: {SIGNAL}
- Working title only; packaging does not make a trademark claim or authorize an irreversible external commitment.
""",
    )
    print(f"Extended fresh submission kit with {TITLE}")


def pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow is required for Race Call image generation") from exc
    return Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False):
    _, _, ImageFont = pillow()
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def center_text(draw, xy: tuple[float, float], text: str, fnt, fill=(245, 247, 250)) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    width = box[2] - box[0]
    height = box[3] - box[1]
    draw.text((xy[0] - width / 2, xy[1] - height / 2), text, font=fnt, fill=fill)


def draw_scene(size: tuple[int, int], t: float, cover: bool = False):
    Image, ImageDraw, _ = pillow()
    bg = (9, 13, 23)
    panel = (18, 26, 42)
    lane = (30, 41, 61)
    white = (245, 247, 250)
    muted = (154, 164, 182)
    cyan = (82, 196, 255)
    gold = (247, 190, 68)
    green = (76, 213, 130)

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    w, h = size
    unit = min(w, h)
    margin = int(unit * 0.065)
    draw.rounded_rectangle((margin, margin, w - margin, h - margin), radius=int(unit * 0.04), fill=panel)
    center_text(draw, (w / 2, margin * 1.8), "RACE CALL", font(int(unit * (0.11 if h <= w else 0.085)), True), white)
    center_text(draw, (w / 2, h * 0.24), "WHO GETS THERE FIRST?", font(int(unit * 0.039), True), muted)

    left = w * 0.13
    finish = w * 0.84
    top_y = h * 0.46
    bottom_y = h * 0.67
    lane_h = max(26, int(unit * 0.075))
    for y in (top_y, bottom_y):
        draw.rounded_rectangle((left, y - lane_h / 2, finish, y + lane_h / 2), radius=int(lane_h / 2), fill=lane)
    finish_w = max(4, int(unit * 0.009))
    draw.rectangle((finish - finish_w / 2, top_y - lane_h * 0.75, finish + finish_w / 2, bottom_y + lane_h * 0.75), fill=white)
    for i in range(8):
        y0 = top_y - lane_h * 0.74 + i * (bottom_y - top_y + lane_h * 1.48) / 8
        if i % 2 == 0:
            draw.rectangle((finish - finish_w * 1.5, y0, finish + finish_w * 1.5, y0 + lane_h * 0.35), fill=(35, 42, 53))

    if cover:
        top_x = left + (finish - left) * 0.20
        bottom_x = left + (finish - left) * 0.36
        label = "CALL IT BEFORE THEY MOVE"
    else:
        phase = t % 4.4
        motion = min(1.0, max(0.0, (phase - 0.75) / 2.8))
        motion = motion * motion * (3 - 2 * motion)
        round_index = int(t / 4.4)
        top_start = 0.08 + (round_index % 3) * 0.035
        bottom_start = 0.22 - (round_index % 2) * 0.045
        top_speed = 0.92 + (round_index % 4) * 0.035
        bottom_speed = 0.78 + ((round_index + 2) % 4) * 0.045
        top_x = left + (finish - left) * min(1.0, top_start + top_speed * motion)
        bottom_x = left + (finish - left) * min(1.0, bottom_start + bottom_speed * motion)
        if phase < 0.75:
            label = "TOP OR BOTTOM?"
        elif phase > 3.7:
            top_time = (1.0 - top_start) / top_speed
            bottom_time = (1.0 - bottom_start) / bottom_speed
            label = "TOP WINS" if top_time < bottom_time else "BOTTOM WINS"
        else:
            label = "WATCH THE REVEAL"

    r = max(11, int(unit * 0.03))
    draw.ellipse((top_x - r, top_y - r, top_x + r, top_y + r), fill=cyan, outline=white, width=max(2, int(unit * 0.003)))
    draw.ellipse((bottom_x - r, bottom_y - r, bottom_x + r, bottom_y + r), fill=gold, outline=white, width=max(2, int(unit * 0.003)))
    center_text(draw, (left + unit * 0.035, top_y), "1", font(int(unit * 0.032), True), white)
    center_text(draw, (left + unit * 0.035, bottom_y), "2", font(int(unit * 0.032), True), white)

    label_color = green if "WINS" in label else white
    center_text(draw, (w / 2, h * 0.82), label, font(int(unit * 0.042), True), label_color)
    if cover:
        center_text(draw, (w / 2, h * 0.90), "HEAD START  +  SPEED  +  INSTINCT", font(int(unit * 0.027), True), muted)
    else:
        score = max(0, int(t * 180))
        seconds = max(0, 30 - int(t))
        center_text(draw, (w / 2, h * 0.91), f"{score} SCORE  •  {seconds}s", font(int(unit * 0.028), True), muted)
    return img


def save_png(img, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)
    if path.stat().st_size == 0:
        raise RuntimeError(f"Generated empty image: {path}")


def build_itch() -> None:
    src = candidate_zip()
    if not ITCH_OUT.exists():
        raise RuntimeError("Base itch.io kit is missing; run build_fresh_itch_release_kit.py first")
    game_dir = ITCH_OUT / SLUG
    if game_dir.exists():
        shutil.rmtree(game_dir)
    game_dir.mkdir(parents=True)
    shutil.copy2(src, game_dir / "game.zip")
    save_png(draw_scene((630, 500), 0.0, cover=True), game_dir / "cover.png")
    for idx, t in enumerate((1.3, 3.2, 5.8, 9.4), start=1):
        save_png(draw_scene((1280, 720), t, cover=False), game_dir / f"screenshot-{idx:02d}.png")

    listing = "\n".join([
        f"Title: {TITLE}",
        "Short description: Compare head starts and speed, then call which racer reaches the finish first.",
        "Kind of project: HTML",
        "Release status: Released",
        "Pricing: Free / no paid access required",
        "Mobile friendly: Yes",
        "Embed: Click to launch in fullscreen",
        "Fullscreen button: Yes",
        "Description: A fast browser prediction game. Two racers start from different positions and move at different speeds toward the same finish. Call Top or Bottom before the decision window closes, then watch the race reveal the answer. Correct calls build score and streak; replay immediately or send a score challenge to a friend.",
        "Controls: Tap / click; keyboard 1 or Up Arrow for Top, 2 or Down Arrow for Bottom",
        "Suggested tags: Skill, Prediction, High Score, Casual, One Button",
        "Language: English",
        "Cash spend: EUR 0",
        f"Signal to watch: {SIGNAL}",
        "",
        "Operator note: upload game.zip, cover.png and all four screenshots. Keep metadata accurate and do not add unrelated discovery tags.",
    ]) + "\n"
    (game_dir / "listing.txt").write_text(listing, encoding="utf-8")

    rewrite_csv(
        ITCH_OUT / "manifest.csv",
        {
            "priority": 9,
            "slug": SLUG,
            "title": TITLE,
            "status": "READY",
            "game_zip": f"{SLUG}/game.zip",
            "cover": f"{SLUG}/cover.png",
            "screenshots": 4,
            "cash_spend_eur": 0,
            "signal_to_watch": SIGNAL,
        },
    )
    append_readme(
        ITCH_OUT / "README.md",
        "Race Call extension:",
        """
Race Call extension:
- validated HTML5 ZIP
- 630x500 discovery cover
- four 1280x720 screenshots
- copy-ready listing text
- working title only; packaging does not make a trademark claim or authorize an irreversible external commitment.
""",
    )
    print(f"Extended itch.io release kit with {TITLE}")


def encode_preview(render_size: tuple[int, int], output_size: tuple[int, int], path: Path) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required for Race Call preview videos")
    path.parent.mkdir(parents=True, exist_ok=True)
    fps = 12
    duration = 15
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{render_size[0]}x{render_size[1]}",
        "-r", str(fps), "-i", "-",
        "-an",
        "-vf", f"scale={output_size[0]}:{output_size[1]}:flags=lanczos",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame in range(fps * duration):
            seconds = frame / fps
            cover = seconds < 0.85
            img = draw_scene(render_size, max(0.0, seconds - 0.85), cover=cover)
            proc.stdin.write(img.tobytes())
    finally:
        proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg failed for {SLUG}: {path}")
    if path.stat().st_size == 0 or path.stat().st_size > 50 * 1024 * 1024:
        raise RuntimeError(f"Invalid preview video: {path}")


def build_portal() -> None:
    if not PORTAL_OUT.exists():
        raise RuntimeError("Base portal asset kit is missing; run build_fresh_portal_assets.py first")
    game_dir = PORTAL_OUT / SLUG
    if game_dir.exists():
        shutil.rmtree(game_dir)
    game_dir.mkdir(parents=True)

    cover_sizes = {
        "landscape": (1920, 1080),
        "portrait": (800, 1200),
        "square": (800, 800),
    }
    for label, size in cover_sizes.items():
        path = game_dir / f"cover-{label}.png"
        save_png(draw_scene(size, 0.0, cover=True), path)
        if path.stat().st_size > 5 * 1024 * 1024:
            raise RuntimeError(f"Cover exceeds 5 MB: {path}")

    video_specs = {
        "landscape": ((960, 540), (1920, 1080)),
        "portrait": ((540, 810), (1080, 1620)),
    }
    for label, (render_size, output_size) in video_specs.items():
        encode_preview(render_size, output_size, game_dir / f"preview-{label}.mp4")

    rewrite_csv(
        PORTAL_OUT / "asset-manifest.csv",
        {
            "slug": SLUG,
            "title": TITLE,
            "landscape_cover": f"{SLUG}/cover-landscape.png",
            "portrait_cover": f"{SLUG}/cover-portrait.png",
            "square_cover": f"{SLUG}/cover-square.png",
            "landscape_preview": f"{SLUG}/preview-landscape.mp4",
            "portrait_preview": f"{SLUG}/preview-portrait.mp4",
            "signal_to_watch": SIGNAL,
            "cash_spend_eur": 0,
        },
    )
    append_readme(
        PORTAL_OUT / "README.md",
        "Race Call extension:",
        """
Race Call extension:
- same zero-cash cover set and silent 15-second previews
- race-prediction artwork generated locally from the mechanic
- working title only; packaging does not make a trademark claim
""",
    )
    print(f"Extended fresh portal asset kit with {TITLE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extend zero-cash handoff kits with Race Call")
    parser.add_argument("mode", choices=("submission", "itch", "portal"))
    args = parser.parse_args()
    if args.mode == "submission":
        build_submission()
    elif args.mode == "itch":
        build_itch()
    else:
        build_portal()


if __name__ == "__main__":
    main()
