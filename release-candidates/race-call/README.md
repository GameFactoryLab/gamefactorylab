# Race Call

Working-title GameFactoryLab release candidate for zero-cash discovery and rapid commercial signal testing.

## Mechanic

Two racers start from different positions and move at different speeds toward the same finish. The player must predict which racer arrives first before the short call window closes, then watches the result play out. Each 30-second run gradually tightens the decision window and produces closer speed-versus-head-start tradeoffs.

This is intentionally distinct from the current timing, catch/dodge, sequence-memory, spatial-transform, visual-tracking, midpoint-estimation, hidden-trajectory and continuous mental-tally candidates. The core skill is intuitive rate-time prediction under a short decision deadline.

## Commercial hypothesis

The mechanic is one-tap, language-light, instantly legible on mobile, produces a visible reveal after every prediction, and naturally supports score challenges. The complete build is one self-contained HTML file with no runtime backend or paid dependency, so it is cheap to expose and kill quickly if replay is weak.

Primary signal order:
1. completed 30-second runs
2. immediate replay rate
3. correct predictions / streak and rounds per run
4. score-challenge shares and challenge opens

Do not spend additional production effort unless comparable free traffic shows stronger replay, session depth or sharing than weaker portfolio candidates. Use the same >=100 comparable-session hard kill/rework gate unless an external portal decides sooner.

## Controls

- Tap/click Top or Bottom before the call window closes.
- Keyboard: `1` / Up Arrow for Top, `2` / Down Arrow for Bottom.
- Space starts a run when idle.
- No account or install required.

## Zero-cash / legal guard

- Cash spend: EUR 0.
- No external runtime assets, paid SDKs, analytics vendors, ads, hosting service, subscription, contractor or backend.
- Local best score and lightweight local metrics only.
- `?score=` creates a reversible friend challenge URL.
- **Race Call is a working title only and is not a trademark claim.**
- No portal terms, new account commitment or irreversible external submission is accepted by this candidate commit.
