# Game Factory Android Factory

Zero-cash Android packaging for the existing GameFactoryLab HTML5 portfolio.

## Current outputs

The same native WebView/share shell produces:

- one portfolio app containing all live games + Labs
- standalone installable Android APKs for selected games
- unique application IDs, so standalone games can coexist on one phone

The first priority batch is tracked in `game_catalog.json`:

- Color Stack Sort
- Ring Pins
- Circuit Flow
- Route Once
- Pixel Logic
- Orbit Align
- Sum Vault

## Architecture

`prepare_assets.py` supports either the full portfolio or one selected game. Standalone builds preserve each HTML5 game's original directory depth so existing `../../core.css` and `../../core.js` references remain valid.

Gradle properties control each standalone identity:

```
-PgameSlug=color-stack-sort
-PgameSource=games
-PgameTitle="Color Stack Sort"
-PgameAppId=com.gamefactorylab.colorstacksort
```

The Android activity launches the selected source directly through `BuildConfig.GAME_START`.

## Release factory

`.github/workflows/android-mobile.yml` builds the portfolio APK and the priority standalone APKs in parallel. Each standalone output gets its own artifact and application ID. Adding another title requires only a validated source folder plus a catalog/workflow entry; no new native code is needed.

## Zero-cash policy

- no Play Console registration
- no paid app-store publishing
- no ad SDK or ad-network account
- no paid hosting
- no paid assets
- no subscription or contractor dependency
- no Internet permission in the APK

External sharing still uses Android's native share sheet. Store signing, ad-network terms and any legally binding distribution terms remain owner approval gates.

## Commercial operating rule

Build fast, sideload-test first, and allocate deeper mobile work only after replay, completion, sharing or retention signals justify it. The factory exists so one mobile release per day is a floor rather than a ceiling.
