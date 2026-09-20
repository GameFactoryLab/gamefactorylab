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
PORTAL_DIR = DIST / "crazygames-basic"


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


def portal_html(html: str) -> str:
    """Create a portal-safe build with no cross-promotion back to GameFactoryLab."""
    html = html.replace('href="../../core.css"', 'href="./core.css"')
    html = html.replace("href='../../core.css'", "href='./core.css'")
    html = html.replace('src="../../core.js"', 'src="./core.js"')
    html = html.replace("src='../../core.js'", "src='./core.js'")
    html = re.sub(
        r'<a\s+href=["\']\.\./\.\./index\.html["\']([^>]*)>(.*?)</a>',
        r'<span\1>\2</span>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return html


def portal_core(core_js: str) -> str:
    """Disable portfolio cross-promotion and keep sharing on the host portal URL."""
    core_js = core_js.replace(
        "const init=()=>{ensureContext(id);ensureNext(id)};",
        "const init=()=>{ensureContext(id)};",
    )
    core_js = core_js.replace(
        "      showNext(id);\n",
        "      // Portal build: do not cross-promote other games.\n",
    )
    core_js += r'''

// Portal build override: share the current portal-hosted game, never an external playable URL.
window.GameFactory.share=async function(id,title,text,url){
  window.GameFactory.event(id,'share_attempt');
  const target=location.href;
  if(navigator.share){
    try{
      await navigator.share({title,text,url:target});
      window.GameFactory.event(id,'share_success');
      return 'shared';
    }catch(e){
      if(e&&e.name==='AbortError')return 'cancelled';
    }
  }
  if(navigator.clipboard?.writeText){
    try{
      await navigator.clipboard.writeText(text+' '+target);
      window.GameFactory.event(id,'share_copy');
      return 'copied';
    }catch(e){}
  }
  return 'unsupported';
};
'''
    return core_js


def write_zip(zip_path: Path, html: str, core_css: str, core_js: str, game_dir: Path, index_path: Path) -> None:
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
            raise RuntimeError(f"{zip_path.name} missing: {sorted(missing)}")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    PORTAL_DIR.mkdir(parents=True)

    core_css = (ROOT / "core.css").read_text(encoding="utf-8")
    core_js = (ROOT / "core.js").read_text(encoding="utf-8")
    cg_core_js = portal_core(core_js)
    rows = []
    portal_rows = []

    for game_dir in sorted(p for p in GAMES.iterdir() if p.is_dir()):
        index_path = game_dir / "index.html"
        if not index_path.exists():
            continue

        game_id = game_dir.name
        source_html = index_path.read_text(encoding="utf-8")
        html = standalone_html(source_html)
        cg_html = portal_html(source_html)
        title = extract_meta(html, r"<title>(.*?)</title>", game_id)
        description = extract_meta(
            html,
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
            "Free browser challenge from GameFactoryLab.",
        )

        zip_name = f"GameFactoryLab_{game_id.replace('-', '_')}_itch.zip"
        write_zip(DIST / zip_name, html, core_css, core_js, game_dir, index_path)
        rows.append(
            {
                "game_id": game_id,
                "title": title,
                "description": description,
                "canonical_url": f"{CANONICAL}games/{game_id}/",
                "zip": zip_name,
            }
        )

        portal_zip_name = f"GameFactoryLab_{game_id.replace('-', '_')}_crazygames_basic.zip"
        write_zip(PORTAL_DIR / portal_zip_name, cg_html, core_css, cg_core_js, game_dir, index_path)
        portal_rows.append(
            {
                "game_id": game_id,
                "title": title,
                "description": description,
                "zip": portal_zip_name,
            }
        )

    with (DIST / "distribution-metadata.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["game_id", "title", "description", "canonical_url", "zip"],
        )
        writer.writeheader()
        writer.writerows(rows)

    with (PORTAL_DIR / "distribution-metadata.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["game_id", "title", "description", "zip"],
        )
        writer.writeheader()
        writer.writerows(portal_rows)

    (PORTAL_DIR / "README.txt").write_text(
        "CrazyGames Basic Launch packages.\n"
        "Cross-promotion to GameFactoryLab is removed and sharing stays on the portal-hosted URL.\n"
        "No external ads or CrazyGames SDK are included in these Basic Launch builds.\n"
        "SDK/monetization integration should only be added after a title qualifies for Full Launch.\n",
        encoding="utf-8",
    )

    print(f"Built {len(rows)} itch packages and {len(portal_rows)} CrazyGames Basic packages in {DIST}")


if __name__ == "__main__":
    main()
