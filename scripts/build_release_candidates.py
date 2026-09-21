#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "release-candidates"
OUT = ROOT / "dist-candidates"

REMOTE_ASSET_RE = re.compile(r"(?:src|href)\s*=\s*[\"']https?://", re.I)
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


def fail(message: str) -> None:
    raise SystemExit(f"Release-candidate build failed: {message}")


def validate_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if REMOTE_ASSET_RE.search(text):
        fail(f"remote runtime asset found in {path.relative_to(ROOT)}")
    lower = text.lower()
    for marker in BANNED_MARKERS:
        if marker.lower() in lower:
            fail(f"blocked runtime/placeholder marker {marker!r} in {path.relative_to(ROOT)}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    candidate_dirs = sorted(
        p for p in CANDIDATES.iterdir() if p.is_dir() and (p / "index.html").exists()
    )
    if not candidate_dirs:
        fail("no candidate directories with index.html found")

    manifest = []
    for candidate in candidate_dirs:
        validate_html(candidate / "index.html")
        zip_path = OUT / f"{candidate.name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for file in sorted(candidate.rglob("*")):
                if file.is_file():
                    z.write(file, file.relative_to(candidate).as_posix())
        manifest.append(
            {
                "id": candidate.name,
                "zip": zip_path.name,
                "bytes": zip_path.stat().st_size,
                "sha256": sha256(zip_path),
            }
        )

    (OUT / "manifest.json").write_text(
        json.dumps({"candidates": manifest}, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Built {len(manifest)} zero-cash release candidate package(s)")
    for item in manifest:
        print(f"- {item['id']}: {item['zip']} ({item['bytes']} bytes)")


if __name__ == "__main__":
    main()
