from pathlib import Path
import shutil

ANDROID_DIR = Path(__file__).resolve().parent
REPO_ROOT = ANDROID_DIR.parents[1]
ASSETS_ROOT = ANDROID_DIR / "app" / "src" / "main" / "assets"
WWW = ASSETS_ROOT / "www"

if ASSETS_ROOT.exists():
    shutil.rmtree(ASSETS_ROOT)
WWW.mkdir(parents=True)

required_files = ("index.html", "core.css", "core.js")
optional_files = ("manifest.webmanifest",)

for name in required_files:
    src = REPO_ROOT / name
    if not src.is_file():
        raise SystemExit(f"Missing required web asset: {name}")
    shutil.copy2(src, WWW / name)

for name in optional_files:
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

print(f"Packaged {len(game_indexes)} live games plus Labs into {WWW}")
