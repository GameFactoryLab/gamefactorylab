# Color Stack Sort — CrazyGames Basic Launch submission pack

Status: **READY FOR OWNER PORTAL SUBMISSION**  
Cash spend: **EUR 0**  
Game: **Color Stack Sort**  
Genre: Puzzle / Sorting  
Language: English  
Devices: Desktop, tablet, mobile  
Controls: Tap/click one tube, then another tube to move the top dot. Undo reverses the most recent move. Restart starts a new timed run.  
Orientation: Responsive; landscape and portrait supported.

## Player-facing description

Move colored dots between tubes and sort every stack into a single color before the timer expires. Clear boards quickly to earn extra time, use Undo to recover from a bad move, and chase a higher score over repeat runs.

## Build

Use `GameFactoryLab_color_stack_sort_crazygames_basic.zip` from the `Build distribution packages` artifact.

The Basic Launch build is generated from the reusable Game Factory distribution pipeline. It removes GameFactoryLab cross-promotion and external playable links, keeps sharing on the portal-hosted URL, and contains no external ad SDK.

Validated package from the 2026-09-20 main build:

- ZIP size: 8,488 bytes
- Files: `index.html`, `core.css`, `core.js`
- Initial download is far below CrazyGames' 20 MB mobile-homepage threshold.
- CrazyGames SDK is intentionally not included for Basic Launch. Current CrazyGames documentation says the SDK is optional for Basic Launch and monetization is disabled until Full Launch.

## Submission assets

Prepared zero-cost submission assets:

- `cover_landscape_1920x1080.png`
- `cover_portrait_800x1200.png`
- `cover_square_800x800.png`
- `preview_landscape_1920x1080.mp4` — 16 seconds, silent
- `preview_portrait_1080x1620.mp4` — 16 seconds, silent

The previews start on the matching cover frame and then demonstrate the tube-sorting mechanic. They contain no promotional CTA, store logo, app icon, or audio.

## Basic Launch compliance check

- English UI: yes
- Mouse/touch support: yes
- Responsive desktop/mobile layout: yes
- No custom fullscreen button: yes
- No third-party ads: yes
- No external playable cross-promotion in portal build: yes
- Package size below 20 MB: yes
- PEGI-12-safe theme/content: yes
- External paid dependencies: none

## Portal action — owner approval required

Do **not** submit or accept CrazyGames terms automatically.

Owner action required:

1. Open the CrazyGames Developer Portal.
2. Create a new game submission for Color Stack Sort.
3. Upload the Basic Launch ZIP plus the three covers and two preview videos.
4. Review and accept the current CrazyGames terms only if approved by the owner.
5. Submit to Basic Launch QA.

No CrazyGames-specific SDK integration should be added before Full Launch is offered, unless the portal explicitly requires it.

## Signal to watch

CrazyGames Basic Launch exposes real traffic without paid acquisition. Primary go/no-go signals:

- gameplay conversion
- average playtime
- retention
- session count

Game-specific diagnostics:

- boards cleared per session
- replay rate
- share attempts/success
- timeout rate
- Undo usage

If Color Stack Sort materially outperforms the portfolio baseline, move it to Full Launch integration first. Otherwise keep it shallow and move distribution capacity to the stronger mechanic.

## Current requirements checked 2026-09-20

- https://docs.crazygames.com/
- https://docs.crazygames.com/requirements/intro/
- https://docs.crazygames.com/requirements/technical/
- https://docs.crazygames.com/requirements/gameplay/
- https://docs.crazygames.com/requirements/game-covers/
