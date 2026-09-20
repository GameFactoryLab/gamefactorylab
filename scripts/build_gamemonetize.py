#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "distribution" / "gamemonetize"
DIST = ROOT / "dist-gamemonetize"
PLACEHOLDER = "__GAME_ID__"
MAX_PACKAGE_BYTES = 25 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build reversible GameMonetize preview or activation-ready HTML5 packages."
    )
    parser.add_argument(
        "--candidate",
        help="Optional candidate slug. Omit to build every candidate directory.",
    )
    parser.add_argument(
        "--game-id",
        help="Optional GameMonetize GameId. Requires --candidate and produces an activation-ready ZIP.",
    )
    return parser.parse_args()


def candidate_dirs(slug: str | None) -> list[Path]:
    if slug:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            raise SystemExit("Invalid candidate slug")
        path = SOURCE / slug
        if not (path / "index.html").exists():
            raise SystemExit(f"Candidate not found: {slug}")
        return [path]
    return sorted(
        p for p in SOURCE.iterdir() if p.is_dir() and (p / "index.html").exists()
    )


def validate_game_id(game_id: str) -> str:
    game_id = game_id.strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{8,80}", game_id):
        raise SystemExit("GameId format looks invalid")
    return game_id


def runtime_files(candidate: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(candidate.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(candidate)
        if rel.as_posix() in {"README.md", "submission.md"}:
            continue
        files.append(path)
    return files


def build_zip(candidate: Path, game_id: str | None) -> dict[str, str | int]:
    slug = candidate.name
    index_path = candidate / "index.html"
    submission = candidate / "submission.md"
    if not submission.exists():
        raise SystemExit(f"{slug}: submission.md is required")

    html = index_path.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        raise SystemExit(
            f"{slug}: {PLACEHOLDER} missing; refusing to package an implicitly activated candidate"
        )

    mode = "activation" if game_id else "preview"
    rendered = html.replace(PLACEHOLDER, game_id) if game_id else html
    if game_id and PLACEHOLDER in rendered:
        raise SystemExit(f"{slug}: unresolved GameId placeholder remains")

    zip_name = f"GameFactoryLab_{slug.replace('-', '_')}_gamemonetize_{mode}.zip"
    zip_path = DIST / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("index.html", rendered)
        for path in runtime_files(candidate):
            if path == index_path:
                continue
            archive.write(path, path.relative_to(candidate).as_posix())

    if zip_path.stat().st_size > MAX_PACKAGE_BYTES:
        raise SystemExit(f"{slug}: package exceeds {MAX_PACKAGE_BYTES // 1024 // 1024} MB safety gate")

    with zipfile.ZipFile(zip_path) as check:
        names = set(check.namelist())
        if "index.html" not in names:
            raise SystemExit(f"{slug}: package root is missing index.html")
        packaged_html = check.read("index.html").decode("utf-8")
        if game_id:
            if PLACEHOLDER in packaged_html or game_id not in packaged_html:
                raise SystemExit(f"{slug}: activation package GameId validation failed")
        elif PLACEHOLDER not in packaged_html:
            raise SystemExit(f"{slug}: preview package unexpectedly contains an activated GameId")

    return {
        "candidate": slug,
        "mode": mode,
        "zip": zip_name,
        "bytes": zip_path.stat().st_size,
        "game_id_state": "inserted" if game_id else "approval-required",
    }


def main() -> None:
    args = parse_args()
    game_id = validate_game_id(args.game_id) if args.game_id else None
    if game_id and not args.candidate:
        raise SystemExit("--game-id requires --candidate so one portal GameId cannot leak into multiple games")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    candidates = candidate_dirs(args.candidate)
    if not candidates:
        raise SystemExit("No GameMonetize candidates found")

    rows = [build_zip(candidate, game_id) for candidate in candidates]
    with (DIST / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["candidate", "mode", "zip", "bytes", "game_id_state"],
        )
        writer.writeheader()
        writer.writerows(rows)

    (DIST / "README.txt").write_text(
        "GameFactoryLab GameMonetize candidate packages.\n"
        "Preview ZIPs deliberately retain __GAME_ID__ and are NOT portal-activation packages.\n"
        "Activation ZIPs are only produced when an explicit GameId is supplied for one candidate.\n"
        "Building a ZIP does not accept portal terms, request activation, publish a game, or spend cash.\n",
        encoding="utf-8",
    )

    print(f"Built {len(rows)} GameMonetize {rows[0]['mode']} package(s) in {DIST}")


if __name__ == "__main__":
    main()
