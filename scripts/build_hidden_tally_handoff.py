#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
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
SLUG = "hidden-tally"
TITLE = "Hidden Tally"
SIGNAL = "completed 30-second runs, immediate replay rate, answer accuracy and streak depth, score-challenge share rate"
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
            "priority": 8,
            "slug": SLUG,
            "title": TITLE,
            "category": "Puzzle",
            "short_description": "Remember the starting count, track objects entering and leaving the hidden box, then choose how many remain.",
            "controls": "Tap / click",
            "progress_save": "No cross-device progress required; local best score only.",
            "itch_tags": "Puzzle, Brain, Mental Math, Skill, High Score, Mobile",
            "crazygames_tags": "1 Player, 2D, Brain, Casual, Logic, Skill, Mobile, Mouse, Train your brain",
            "signal_to_watch": SIGNAL,
            "suggested_tags": "Puzzle, Brain, Mental Math, Skill, High Score, Mobile",
            "crazygames_tag_reference_date": CRAZYGAMES_TAG_REFERENCE_DATE,
            "status": "READY",
            "itch_package": f"{SLUG}.zip",
            "crazygames_basic_package": f"{SLUG}.zip",
            "cash_spend_eur": 0,
        },
    )
    append_readme(
        SUBMISSION_OUT / "README.md",
        "Hidden Tally extension:",
        f"""
Hidden Tally extension:
- itch.io upload ZIP: `itch/{SLUG}.zip`
- CrazyGames Basic-safe ZIP: `crazygames-basic/{SLUG}.zip`
- Category: Puzzle
- Controls: Tap / click
- itch.io tags: Puzzle, Brain, Mental Math, Skill, High Score, Mobile
- CrazyGames tags: 1 Player, 2D, Brain, Casual, Logic, Skill, Mobile, Mouse, Train your brain
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
        raise RuntimeError("Pillow is required for Hidden Tally image generation") from exc
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
    bg = (10, 14, 24)
    panel = (20, 28, 44)
    white = (245, 247, 250)
    muted = (152, 162, 179)
    cyan = (84, 190, 255)
    gold = (245, 188, 66)
    green = (73, 209, 126)
    purple = (99, 102, 241)

    img = Image.new("RGB", size, bg)
    draw = ImageDraw.Draw(img)
    w, h = size
    unit = min(w, h)
    margin = int(unit * 0.07)
    draw.rounded_rectangle((margin, margin, w - margin, h - margin), radius=int(unit * 0.04), fill=panel)
    center_text(draw, (w / 2, margin * 1.9), "HIDDEN TALLY", font(int(unit * (0.105 if h <= w else 0.082)), True), white)
    center_text(draw, (w / 2, h * 0.25), "KEEP THE COUNT IN YOUR HEAD", font(int(unit * 0.039), True), muted)

    box_left = w * 0.30
    box_right = w * 0.70
    box_top = h * 0.38
    box_bottom = h * 0.74
    draw.rounded_rectangle((box_left, box_top, box_right, box_bottom), radius=max(16, int(unit * 0.025)), fill=(17, 24, 39), outline=purple, width=max(3, int(unit * 0.006)))
    center_text(draw, (w / 2, box_top + (box_bottom - box_top) * 0.22), "HIDDEN BOX", font(int(unit * 0.033), True), (165, 180, 252))

    if cover:
        center_text(draw, (w / 2, (box_top + box_bottom) / 2 + unit * 0.02), "4", font(int(unit * 0.15), True), white)
        center_text(draw, (w / 2, box_bottom - unit * 0.05), "STARTING COUNT", font(int(unit * 0.026), True), muted)
        return img

    cycle = t % 3.6
    event_index = int(t / 1.05)
    entering = event_index % 3 != 2
    progress = min(1.0, (cycle % 1.05) / 1.05)
    progress = progress * progress * (3 - 2 * progress)
    y = (box_top + box_bottom) / 2
    left_outer = w * 0.12
    right_outer = w * 0.88
    if entering:
        x = left_outer + (w / 2 - left_outer) * progress
        color = cyan
        label = "+1 ENTERED"
    else:
        x = w / 2 + (right_outer - w / 2) * progress
        color = gold
        label = "−1 LEFT"

    r = max(10, int(unit * 0.025))
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=white, width=max(2, int(unit * 0.003)))
    center_text(draw, (w / 2, box_bottom + unit * 0.07), label, font(int(unit * 0.035), True), color)

    if (t % 4.8) > 3.7:
        answer = 3 + (event_index % 4)
        center_text(draw, (w / 2, (box_top + box_bottom) / 2 + unit * 0.02), "?", font(int(unit * 0.15), True), white)
        center_text(draw, (w / 2, h * 0.88), f"HOW MANY REMAIN?  •  ANSWER {answer}", font(int(unit * 0.031), True), green)
    else:
        score = max(0, int(t * 220))
        seconds = max(0, 30 - int(t))
        center_text(draw, (w / 2, h * 0.88), f"{score} SCORE  •  {seconds}s", font(int(unit * 0.030), True), white)
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
    for idx, t in enumerate((1.4, 4.0, 7.2, 10.6), start=1):
        save_png(draw_scene((1280, 720), t, cover=False), game_dir / f"screenshot-{idx:02d}.png")

    listing = "\n".join([
        f"Title: {TITLE}",
        "Short description: Track objects entering and leaving a hidden box, then choose how many remain.",
        "Kind of project: HTML",
        "Release status: Released",
        "Pricing: Free / no paid access required",
        "Mobile friendly: Yes",
        "Embed: Click to launch in fullscreen",
        "Fullscreen button: Yes",
        "Description: A fast mental-tracking challenge for short browser sessions. Memorize a starting count, follow every object entering or leaving the hidden box, then choose the final quantity before the next round begins. Correct answers build score and streak; replay immediately or send a score challenge to a friend.",
        "Controls: Tap / click",
        "Suggested tags: Puzzle, Brain, Mental Math, Skill, High Score",
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
            "priority": 8,
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
        "Hidden Tally extension:",
        """
Hidden Tally extension:
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
        raise RuntimeError("ffmpeg is required for Hidden Tally preview videos")
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
        "Hidden Tally extension:",
        """
Hidden Tally extension:
- same zero-cash cover set and silent 15-second previews
- mental-tracking artwork generated locally from the mechanic
- working title only; packaging does not make a trademark claim
""",
    )
    print(f"Extended fresh portal asset kit with {TITLE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extend zero-cash handoff kits with Hidden Tally")
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
