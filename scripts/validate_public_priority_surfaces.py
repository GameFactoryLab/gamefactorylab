#!/usr/bin/env python3
"""Fail closed when public winner-search surfaces drift from the commercial queue."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP5 = ["lock-line", "catch-drop", "pattern-relay", "mirror-mark", "ring-pins"]
CHALLENGER = "track-three"
STALE_TOP5 = ["circuit-flow", "gravity-flip", "bridge-snap", "cluster-collapse"]


def text(path: str) -> str:
    value = (ROOT / path).read_text(encoding="utf-8")
    if not value.strip():
        raise RuntimeError(f"Empty public surface: {path}")
    return value


def require(path: str, needles: list[str]) -> None:
    body = text(path)
    missing = [needle for needle in needles if needle not in body]
    if missing:
        raise RuntimeError(f"{path} is missing current-priority marker(s): {missing}")


def main() -> None:
    require("top5/index.html", TOP5)
    require("daily/index.html", TOP5)
    require("challenge/index.html", TOP5 + [CHALLENGER, "scoreParam:'score'"])
    require(
        "index.html",
        ["Lock Line", "Catch Drop", "Pattern Relay", "Mirror Mark", "Ring Pins", "Track Three"],
    )

    challenge = text("challenge/index.html")
    leaked = [slug for slug in STALE_TOP5 if f'value="{slug}"' in challenge]
    if leaked:
        raise RuntimeError(
            "Challenge hub is diluting current winner-search traffic into stale Top 5 slots: "
            + ", ".join(leaked)
        )

    sw = text("sw.js")
    for route in ("./top5/", "./challenge/", "./daily/", "./release-candidates/track-three/"):
        if route not in sw:
            raise RuntimeError(f"PWA cache is missing public priority route: {route}")

    print(
        "Validated public winner-search alignment: "
        "5 active commercial candidates + Track Three challenger; stale Top 5 challenge slots blocked."
    )


if __name__ == "__main__":
    main()
