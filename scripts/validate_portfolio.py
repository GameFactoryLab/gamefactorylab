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

    # The homepage is intentionally a focused set of entry funnels instead of a
    # catalogue of every game. Full game coverage is validated below through
    # the sitemap, offline cache and core rotation.
    required_home_funnels = {
        "fresh/",
        "top5/",
        "daily/",
        "challenge/",
        "sprint/",
        "discover/",
        "labs/",
    }
    home_hrefs = set(re.findall(r'href=["\']([^"\']+)["\']', index))
    missing_home_funnels = {
        funnel
        for funnel in required_home_funnels
        if not any(href.split("?", 1)[0] == funnel for href in home_hrefs)
    }
    if missing_home_funnels:
        fail(f"homepage missing funnels: {sorted(missing_home_funnels)}")

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
    schema_items = schema.get("itemListElement", [])
    if schema.get("numberOfItems") != len(schema_items):
        fail(
            f"homepage schema numberOfItems={schema.get('numberOfItems')} "
            f"but contains {len(schema_items)} items"
        )
    if not schema_items:
        fail("homepage ItemList schema has no items")
    schema_positions = [item.get("position") for item in schema_items]
    if schema_positions != list(range(1, len(schema_items) + 1)):
        fail("homepage ItemList schema positions are not sequential")
    invalid_schema_urls = [
        item.get("url", "")
        for item in schema_items
        if not item.get("url", "").startswith(
            "https://gamefactorylab.github.io/gamefactorylab/"
        )
    ]
    if invalid_schema_urls:
        fail(f"homepage ItemList schema has invalid URLs: {invalid_schema_urls}")

    print(
        f"Validated {len(expected)} games across core rotation, sitemap and offline cache; "
        f"validated {len(required_home_funnels)} homepage funnels and schema"
    )


if __name__ == "__main__":
    main()
