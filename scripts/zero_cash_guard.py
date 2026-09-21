#!/usr/bin/env python3
"""Fail CI if a live Game Factory game adds a runtime dependency that can create cost or lock-in.

The live portfolio is intentionally self-contained: HTML, CSS, JavaScript and generated
browser primitives only. Absolute canonical/OG metadata links are fine; runtime-loaded
scripts, stylesheets, media, iframes or remote CSS assets are not.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "games"

RUNTIME_TAG_ATTRS = {
    "script": "src",
    "img": "src",
    "audio": "src",
    "video": "src",
    "source": "src",
    "iframe": "src",
}

FORBIDDEN_RUNTIME_MARKERS = {
    "api.gamemonetize.com": "GameMonetize SDK",
    "sdk.crazygames.com": "CrazyGames SDK",
    "googletagmanager.com": "Google Tag Manager",
    "google-analytics.com": "Google Analytics",
    "doubleclick.net": "DoubleClick",
    "connect.facebook.net": "Meta/Facebook runtime SDK",
    "__GAME_ID__": "unresolved monetization game id",
}


def is_remote(value: str) -> bool:
    v = value.strip().lower()
    return v.startswith("http://") or v.startswith("https://") or v.startswith("//")


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.remote_assets: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag in RUNTIME_TAG_ATTRS:
            attr = RUNTIME_TAG_ATTRS[tag]
            value = data.get(attr, "")
            if value and is_remote(value):
                self.remote_assets.append((f"{tag}[{attr}]", value))
        if tag == "link" and "stylesheet" in data.get("rel", "").lower().split():
            value = data.get("href", "")
            if value and is_remote(value):
                self.remote_assets.append(("link[rel=stylesheet]", value))


def inspect(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    parser = AssetParser()
    parser.feed(text)
    problems = [f"remote runtime asset {kind}: {value}" for kind, value in parser.remote_assets]

    for match in re.finditer(r"url\(\s*['\"]?(https?:)?//", text, flags=re.IGNORECASE):
        problems.append(f"remote CSS url() near byte {match.start()}")

    for match in re.finditer(r"\.(?:src|href)\s*=\s*['\"](?:https?:)?//", text, flags=re.IGNORECASE):
        problems.append(f"dynamic remote asset assignment near byte {match.start()}")

    for marker, label in FORBIDDEN_RUNTIME_MARKERS.items():
        if marker.lower() in text.lower():
            problems.append(f"forbidden runtime marker: {label} ({marker})")

    return problems


def main() -> None:
    game_pages = sorted(GAMES.glob("*/index.html"))
    if not game_pages:
        raise SystemExit("Zero-cash guard failed: no live game pages found")

    failures: list[str] = []
    for page in game_pages:
        for problem in inspect(page):
            failures.append(f"{page.relative_to(ROOT)}: {problem}")

    if failures:
        print("Zero-cash guard FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(
        f"Zero-cash guard passed for {len(game_pages)} live games: "
        "no remote runtime assets, ad SDKs, analytics SDKs or unresolved monetization IDs."
    )


if __name__ == "__main__":
    main()
