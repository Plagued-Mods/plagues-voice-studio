# Build validation, v0.2.4

Run on the Linux authoring container, October 16, 2026.

- Python syntax: `python -m compileall -q src scripts tests launcher.py` — PASS.
- Headless unit/integration/static review: `pytest -q` — 56 passed.
- ZIP integrity: archive CRC test (performed when releasing).
- PyQt6 not installed in the authoring container; attempted installation was blocked by lack of network access. The Windows GUI was **not** launched or visually verified here.
- Bundled `ui_smoke_test.py` exercises actual frozen Qt main-window construction, three About opens, closing/reopening, branding assets, Help search/filtering, and About tabs. Windows build script blocks installer production if the test fails.
- Actual speech-model generation, CUDA, Bethesda FaceFX, real XWM encoding and in-game FUZ playback have not been verified in this environment.

## Regression / implementation review

- Resolved prior About instability by using `AboutDialog` from a separate module with explicit imports, a persistent parent, and nonblocking `.show()`.
- Export Library's previously faulty host reference remains `self.host`.
- Added read-only library mode to `VoiceLibrary`; opening old v0.1 storage does not create directories there.
- Selected voice persists, model-incompatible vocal tags get a visible warning, model/audio backends were otherwise left unchanged.
- Existing v0.2 user-data/settings identities are retained for continuity; the new executable and installer are distinct.
