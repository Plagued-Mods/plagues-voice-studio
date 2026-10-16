# Experimental 0.3.0-alpha1: build and test validation

Source environment: Linux authoring container, October 16, 2026.

- Frozen **stable v0.2.4 source** preserved independently as an identical ZIP; SHA-256 `23464fb7c541e000d03f2c47f14e18629fe70d97f1b9b4d4ebadf556776d5928`.
- Python syntax: `python -m compileall -q src scripts tests launcher.py optional_engine_runner.py`, verified.
- Python tests: `pytest -q`, including pure-Python JSON IPC mock-runner tests. 65 passed, including 9 optional-engine regression tests.
- ZIP integrity and checksum: performed after building the release archive.
- **PyQt6 is not available in this authoring container.** The experimental Qt app was not rendered on Windows here.
- **Qwen3-TTS and IndexTTS weights and runtimes were not installed or invoked with real voice inference here.** The subprocess protocol and output handling were tested against a simulated isolated interpreter.
- Windows build script will reject a missing or failing frozen-runtime/GUI report, as in earlier versions. The GUI smoke test checks About, Help and the new Engine Lab before permitting archive/installer packaging.
- AMD acceleration, real inference timbre, model performance and in-game Bethesda export are not verified.

## Isolation review

- Experimental source/metadata, application settings, Windows executable, installer identity and per-user data root are separate from v0.2.4.
- Previous v0.2.x and v0.1.x voices are read-only; no hidden migration or writes to stable user data.
- Qwen/Index optional Python packages are not installed or bundled in the Chatterbox environment.
- Child runner processes have explicit executable paths, JSON request/response files, no shell string or HTTP listener, and cancellation/timeout support.
- Character profiles and generation sidecars are saved in experimental paths only.

## Limitations

No native Windows EXE has been generated here. Upstream TTS APIs, especially IndexTTS's CPU support, may require a local compatibility patch as APIs change. This release is a development alpha, **not a production replacement**.
