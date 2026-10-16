# Plague's Voice Studio 0.2.4 — Interface refinement and usability review

## Redesigned UI

- Refined dark charcoal / radioactive-green styling with clearer focus rings, controls, consistent spacing and more legible text.
- Main header uses the plague-doctor icon, title and creator byline with prominent Help and About actions.
- Help tab replaced by a **searchable, topic-based help center** with getting started, models/voices, narration tags, export library, Bethesda conversion, build troubleshooting, and licensing. Includes adjustable Help text size and the F1 keyboard shortcut.
- About dialog replaced by a **stable, nonmodal** tabbed presentation: Overview, Credits & licenses, and local diagnostics with Copy diagnostics. The full logo appears in the branded header, and the icon remains the window/application icon. No nested Qt event loop, model loading, or internet needed to open it.

## Reliability and feature improvements

- Fixed missing `QDialog` import from the shipped v0.2.3 source via a separate `AboutDialog` implementation; strengthened the packaged GUI smoke test to click About repeatedly and check Help filtering and tabs.
- For Original English and Multilingual V3, scripts containing common Turbo/Nano vocal-event tags now show a **non-destructive warning** rather than silently proceeding without feedback.
- The selected narration voice now persists between launches in the existing v0.2 settings identity.
- Legacy v0.1 voice libraries are truly read-only, including construction: no files or folders are created in them on launch.
- Added `PREVIEW_GUI.bat` to preview source UI changes **without rebuilding PyInstaller**; requires a prepared `.venv-build` or `.venv` in the current source directory.
- Keeps the working v0.2 settings/data folder (`PlaguesVoiceStudio-v021` / `PlaguesVoiceStudio021`) so existing voices and projects remain accessible. The packaged v0.2.4 executable/installer have new names to avoid overwriting the previous executable.

## Testing

- Source Python compilation and automated tests: see build report.
- The Windows build uses frozen runtime and GUI smoke tests; a package will not be distributed if either fails.
- **No native Windows executable or in-game Bethesda conversion was tested in this Linux build environment.** Real speech generation and external FaceFX/xWMA tools must still be tested by the user.

## Potential future work (intentionally not added in this UI-focused release)

- Audio waveform with seek markers and A/B comparison of generations.
- Explicit model memory unload / memory-use feedback for CPU systems.
- Persistent narration drafts and queue sessions (with safe recovery after crashes).
- First-run diagnostic and setup assistant for game conversion tools.
