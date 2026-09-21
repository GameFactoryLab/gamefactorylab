from pathlib import Path
import json
import re
import sys

ANDROID_DIR = Path(__file__).resolve().parent
REPO_ROOT = ANDROID_DIR.parents[1]
CATALOG = ANDROID_DIR / "game_catalog.json"
MANIFEST = ANDROID_DIR / "app" / "src" / "main" / "AndroidManifest.xml"

data = json.loads(CATALOG.read_text(encoding="utf-8"))
games = data.get("games", [])

if not games:
    raise SystemExit("Catalog contains no games")

seen_slugs = set()
seen_ids = set()
errors = []

for game in games:
    slug = game.get("slug", "")
    source = game.get("source", "")
    title = game.get("title", "")
    app_id = game.get("app_id", "")

    if not slug or slug in seen_slugs:
        errors.append(f"invalid/duplicate slug: {slug!r}")
    seen_slugs.add(slug)

    if source not in {"games", "release-candidates"}:
        errors.append(f"{slug}: unsupported source {source!r}")

    if not title.strip():
        errors.append(f"{slug}: missing title")

    if not re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+", app_id):
        errors.append(f"{slug}: invalid app_id {app_id!r}")
    if app_id in seen_ids:
        errors.append(f"{slug}: duplicate app_id {app_id!r}")
    seen_ids.add(app_id)

    index = REPO_ROOT / source / slug / "index.html"
    if not index.is_file():
        errors.append(f"{slug}: missing source {index.relative_to(REPO_ROOT)}")

manifest_text = MANIFEST.read_text(encoding="utf-8")
if "android.permission.INTERNET" in manifest_text:
    errors.append("Android manifest must stay offline-only: INTERNET permission found")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)

auto = [g["slug"] for g in games if g.get("auto_build")]
print(f"Catalog valid: {len(games)} targets; {len(auto)} auto-build targets")
print("Auto-build:", ", ".join(auto))
