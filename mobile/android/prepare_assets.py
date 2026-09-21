from pathlib import Path
import argparse
import shutil

ANDROID_DIR = Path(__file__).resolve().parent
REPO_ROOT = ANDROID_DIR.parents[1]
ASSETS_ROOT = ANDROID_DIR / "app" / "src" / "main" / "assets"
WWW = ASSETS_ROOT / "www"

parser = argparse.ArgumentParser()
parser.add_argument("--game-slug", default="portfolio")
parser.add_argument("--game-source", choices=("portfolio", "games", "release-candidates"), default="portfolio")
args = parser.parse_args()

if ASSETS_ROOT.exists():
    shutil.rmtree(ASSETS_ROOT)
WWW.mkdir(parents=True)

for name in ("core.css", "core.js"):
    src = REPO_ROOT / name
    if not src.is_file():
        raise SystemExit(f"Missing required shared asset: {name}")
    shutil.copy2(src, WWW / name)

if args.game_slug == "portfolio" or args.game_source == "portfolio":
    for name in ("index.html", "manifest.webmanifest"):
        src = REPO_ROOT / name
        if src.is_file():
            shutil.copy2(src, WWW / name)

    for dirname in ("games", "sprint", "labs", "release-candidates"):
        src = REPO_ROOT / dirname
        if src.is_dir():
            shutil.copytree(src, WWW / dirname)

    game_indexes = sorted((WWW / "games").glob("*/index.html"))
    if len(game_indexes) < 27:
        raise SystemExit(f"Expected at least 27 packaged games, found {len(game_indexes)}")
    print(f"Packaged portfolio with {len(game_indexes)} live games plus Labs")
else:
    source_dir = REPO_ROOT / args.game_source / args.game_slug
    index = source_dir / "index.html"
    if not index.is_file():
        raise SystemExit(f"Game source missing: {index}")

    target_dir = WWW / args.game_source / args.game_slug
    shutil.copytree(source_dir, target_dir)

    target = f"{args.game_source}/{args.game_slug}/index.html?app=android"
    (WWW / "index.html").write_text(
        "<!doctype html><meta charset='utf-8'>"
        f"<meta http-equiv='refresh' content='0;url={target}'>"
        f"<script>location.replace('{target}')</script>",
        encoding="utf-8",
    )
    print(f"Packaged single mobile game: {args.game_source}/{args.game_slug}")
