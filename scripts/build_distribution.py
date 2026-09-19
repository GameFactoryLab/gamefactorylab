#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "games"
DIST = ROOT / "dist"
CANONICAL = "https://gamefactorylab.github.io/gamefactorylab/"


def extract_meta(html: str, pattern: str, fallback: str) -> str:
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else fallback


def standalone_html(html: str) -> str:
    html = html.replace('href="../../core.css"', 'href="./core.css"')
    html = html.replace("href='../../core.css'", "href='./core.css'")
    html = html.replace('src="../../core.js"', 'src="./core.js"')
    html = html.replace("src='../../core.js'", "src='./core.js'")
    html = html.replace('href="../../index.html"', f'href="{CANONICAL}"')
    html = html.replace("href='../../index.html'", f"href='{CANONICAL}'")
    return html


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    core_css = (ROOT / "core.css").read_text(encoding="utf-8")
    core_js = (ROOT / "core.js").read_text(encoding="utf-8")
    rows = []

    for game_dir in sorted(p for p in GAMES.iterdir() if p.is_dir()):
        index_path = game_dir / "index.html"
        if not index_path.exists():
            continue

        game_id = game_dir.name
        source_html = index_path.read_text(encoding="utf-8")
        html = standalone_html(source_html)
        title = extract_meta(html, r"<title>(.*?)</title>", game_id)
        description = extract_meta(
            html,
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
            "Free browser challenge from GameFactoryLab.",
        )
        zip_name = f"GameFactoryLab_{game_id.replace('-', '_')}_itch.zip"
        zip_path = DIST / zip_name

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("index.html", html)
            archive.writestr("core.css", core_css)
            archive.writestr("core.js", core_js)
            for asset in sorted(game_dir.rglob("*")):
                if not asset.is_file() or asset == index_path:
                    continue
                archive.write(asset, asset.relative_to(game_dir).as_posix())

        with zipfile.ZipFile(zip_path) as check:
            names = set(check.namelist())
            required = {"index.html", "core.css", "core.js"}
            missing = required - names
            if missing:
                raise RuntimeError(f"{zip_name} missing: {sorted(missing)}")

        rows.append(
            {
                "game_id": game_id,
                "title": title,
                "description": description,
                "canonical_url": f"{CANONICAL}games/{game_id}/",
                "zip": zip_name,
            }
        )

    with (DIST / "distribution-metadata.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["game_id", "title", "description", "canonical_url", "zip"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Built {len(rows)} standalone game packages in {DIST}")


if __name__ == "__main__":
    main()
