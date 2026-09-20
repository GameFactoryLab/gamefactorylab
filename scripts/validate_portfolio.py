#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "games"


def fail(message: str) -> None:
    raise SystemExit(f"Portfolio validation failed: {message}")


def main() -> None:
    game_ids = sorted(
        p.name for p in GAMES.iterdir() if p.is_dir() and (p / "index.html").exists()
    )
    expected = set(game_ids)
    if not expected:
        fail("no playable game directories found")

    index = (ROOT / "index.html").read_text(encoding="utf-8")
    core = (ROOT / "core.js").read_text(encoding="utf-8")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sw = (ROOT / "sw.js").read_text(encoding="utf-8")

    home_ids = set(re.findall(r'href=["\']games/([^/]+)/index\.html["\']', index))
    missing_home = expected - home_ids
    if missing_home:
        fail(f"homepage missing games: {sorted(missing_home)}")

    missing_sitemap = {
        game_id
        for game_id in expected
        if f"/games/{game_id}/</loc>" not in sitemap
    }
    if missing_sitemap:
        fail(f"sitemap missing games: {sorted(missing_sitemap)}")

    missing_cache = {
        game_id
        for game_id in expected
        if f"'./games/{game_id}/'" not in sw and f'"./games/{game_id}/"' not in sw
    }
    if missing_cache:
        fail(f"service-worker cache missing games: {sorted(missing_cache)}")

    core_ids = set(re.findall(r"id:'([^']+)'", core))
    missing_core = expected - core_ids
    if missing_core:
        fail(f"core portfolio rotation missing games: {sorted(missing_core)}")

    required_core_markers = [
        "const sprintGames=[",
        "const portfolioGames=[",
        "const pool=sprintGames.slice();",
        "portfolioGames.findIndex",
    ]
    for marker in required_core_markers:
        if marker not in core:
            fail(f"core rotation marker missing: {marker}")

    schema_match = re.search(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        index,
        re.DOTALL,
    )
    if not schema_match:
        fail("homepage ItemList schema missing")
    schema = json.loads(schema_match.group(1))
    if schema.get("numberOfItems") != len(expected):
        fail(
            f"schema numberOfItems={schema.get('numberOfItems')} but disk has {len(expected)} games"
        )

    schema_ids = {
        match.group(1)
        for item in schema.get("itemListElement", [])
        if (match := re.search(r"/games/([^/]+)/", item.get("url", "")))
    }
    if schema_ids != expected:
        fail(
            f"schema game set mismatch; missing={sorted(expected-schema_ids)}, extra={sorted(schema_ids-expected)}"
        )

    print(
        f"Validated {len(expected)} games across homepage, core rotation, sitemap, offline cache and schema"
    )


if __name__ == "__main__":
    main()
