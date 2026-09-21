# Game Factory Quick Games — Android

Zero-cash Android wrapper for the existing GameFactoryLab HTML5 portfolio.

## What it does

- Packages the live HTML5 games locally into an Android APK.
- Runs without paid hosting or paid runtime dependencies.
- Reuses the same game code as the web portfolio.
- Preserves local score/progress storage through Android WebView.
- Provides a native Android share sheet through the existing GameFactoryNative bridge.
- Automatically includes new live games in future builds.

## Build

The GitHub Actions workflow `android-mobile.yml` uses:

- JDK 17
- Gradle 9.6
- Android SDK 36
- Android Gradle Plugin 9.4

The workflow first runs `prepare_assets.py`, then builds an installable debug APK and publishes it as the `gamefactory-quick-games-android` artifact.

## Zero-cash commercial policy

This mobile build intentionally contains no paid advertising SDK, subscription, paid asset, paid hosting dependency or app-store commitment.

Google Play registration, production signing/account commitments and ad-network terms remain explicit owner-approval gates. Until Game Factory has realized cash flow, APK distribution stays on zero-cost channels.
