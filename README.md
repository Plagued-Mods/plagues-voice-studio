# Plague's Voice Studio 0.2.4

**Created by Kaotick Jay**  
Local Chatterbox narration, Fallout 4 / Skyrim voice packaging, and direct mod deployment.

## Standalone release, not an in-place upgrade

This is an **independent v0.2.4 application source release** based on the working v0.1.3 code and the v0.1.4 export preview. It does **not** replace the existing installation. To keep both builds side by side:

- New Windows executable: `PlaguesVoiceStudio024.exe`.
- New Inno Setup identity, start menu group, and installation directory: `Plague's Voice Studio 0.2`.
- New per-user settings identity: `KaotickJay/PlaguesVoiceStudio021`.
- New data folder: `%LOCALAPPDATA%\PlaguesVoiceStudio-v021` (Linux uses `~/.local/share/PlaguesVoiceStudio-v021`).
- v0.1.x voice references are **listed read-only** alongside newly imported v0.2 voices. Deleting a legacy voice is blocked. New voices and saved profiles are written only to the v0.2 data directory.
- The Export Library automatically offers `Music\Chatterbox Studio` and the older program's `exports` folder, plus v0.2 exports. User-selected folders are supported.
- Default narration exports use `Music\Plague's Voice Studio 0.2` where the Music directory exists, or the v0.2 data folder otherwise.

**Existing v0.2 voice libraries, saved mod profiles and preferences are reused** under `PlaguesVoiceStudio-v021` and `PlaguesVoiceStudio021`; no migration or copying is required. Older v0.1 data is only read, never changed.

**No game, mod, or plugin files are provided, and existing programs and datasets are not migrated or overwritten.**

## What's new in v0.2.4

- Redesigned dark GUI with stronger keyboard-focus indicators, clearer spacing and branded header.
- Searchable Help center with seven sections, model/tag guidance, game export documentation and adjustable reading size. Press **F1** to open it.
- Modern About dialog with full artwork, overview, credits/licensing, and copyable local diagnostics. No model load is required to open it.
- Warns when non-native vocal-event tags are entered for Original English or Multilingual V3. It never removes the user's text.
- Remembers the last selected voice. Legacy v0.1 voice references are read-only, including at the filesystem level.
- Source GUI preview: once this source folder has a working `.venv-build` or `.venv`, run `PREVIEW_GUI.bat` to inspect UI without rerunning PyInstaller. **Always rebuild to update a packaged EXE.**

See `RELEASE_NOTES_0.2.4.md` for details.

## Core features

### Voice-based filenames

A new narration defaults to `<VoiceName>_narration_YYYYMMDD-HHMMSS.wav`, e.g. `Mama_Mire_narration_20261015-174812.wav`, or `default_narration_YYYYMMDD-HHMMSS.wav` with no named voice. Invalid filename characters become underscores. The MP3 setting produces `.mp3` instead; collisions append `_2`, `_3` etc. The explicitly chosen output filename takes precedence.

### Export Library

Select the **Export Library** tab to browse, sort, double-click and play any WAV/MP3 (plus FLAC/OGG/M4A where Qt multimedia codecs support them) in a selected export directory. Add directories, refresh after rendering, open a file's folder, or send a selected audio recording directly into the Bethesda export form. The older "Play last result" button remains usable.

### Bethesda projects and voice assignments

1. In **Bethesda Voice Export**, choose the game, enter the owning plugin filename and select a target folder.
2. Select **Game Data folder** for the actual game's `...\Data` directory. Or select **MO2 mod root** for `...\mods\YourMod`. Both contain `Sound\Voice` directly, with no extra `Data` directory.
3. Click **Save project**. Each project can store one or more **Voice Profiles** mapping an exact Creation Kit `VoiceType` EditorID to a Chatterbox model and imported or legacy reference voice.
4. In the Narration tab, synthesize dialogue, then use **Last narration** or select an older export. Paste the exact spoken transcript used to animate the mouth.
5. Supply the exact **response filename from CK**. The app does not inspect or modify plugins; the filename cannot be safely inferred from the voice sample.
6. Configure `FaceFXWrapper.exe`, `FonixData.cdf`, a supported xWMA encoder, and optionally FFmpeg. Select the correct target game (Fallout 4, Skyrim, Skyrim SE/AE). Those binaries and Bethesda data are **not included**.
7. Review the **full destination path**. Press **Build ... and install**. If the target FUZ exists, confirm replacement. The original is backed up under the v0.2 project-data directory before atomic installation.

**Fallout 4 example:** `C:\Games\Fallout 4\Data\Sound\Voice\MyMod.esp\MyNPCVoice\000F1B2C_1.fuz`

**MO2 example:** `D:\MO2\mods\MyMod\Sound\Voice\MyMod.esp\MyNPCVoice\000F1B2C_1.fuz`

Note that the *owning* plugin can be a master, not necessarily the currently edited mod. Skyrim uses its own CK-provided response filename format. Passing that exact filename avoids guessing the truncation and naming rules.

### Game voice conversion pipeline

Source WAV/MP3 -> FFmpeg-generated **16 kHz mono PCM WAV** -> FaceFXWrapper game-specific **LIP**; independently -> **44.1 kHz mono PCM WAV** -> xWMA encoder **XWM** -> internal **FUZ** packer. It structurally verifies the result before direct deployment. Intermediate WAV, XWM, LIP and transcript are stored outside the game if "Keep intermediates" is enabled.

#### External components

- FaceFXWrapper: https://github.com/Nukem9/FaceFXWrapper . Requires legitimate local CK/Fonix assets; Bethesda-derived portions have additional license requirements.
- WMAEncodeRS: https://github.com/MSIVST/WMAEncodeRS . Supports xWMA using Windows Media Format runtime on Windows 10/11; refer to its license and release notes.
- FFmpeg: bundled indirectly through `imageio-ffmpeg` as a Python dependency, or provide the path of an installed binary.
- Alternatively, use the locally installed Creation Kit's `xwmaencode.exe`.

The installer **does not redistribute** Bethesda's copyrighted components, FonixData.cdf, FaceFXWrapper or the proprietary xWMA encoder. The user locates installed tools once in the form; those tool paths are saved.

## Building / running on Windows

**A Windows build has not been produced in this Linux environment.** The archive contains a distinct standalone Windows build configuration and convenient batch files.

**Quick source launch (requires Python 3.11, Git and a network connection for initial dependencies/model weights):**

```bat
RUN_WINDOWS.bat
```

**Build the actual standalone Windows portable directory and optionally the installer:**

```bat
BUILD_WINDOWS.bat
```

By default the build bundles the Nano model. For an all-model fully offline build, use:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1 -FullOffline
```

This can require substantial disk space and time. Inno Setup 6 is optional; without it the portable ZIP is still produced. Unzip the portable distribution into **its own folder**, never on top of an older v0.1.x executable.

### Linux source development

The PyQt6 app is cross-platform for narration and project management, but WMAEncodeRS uses the Windows Media runtime, and FaceFX/CK tool execution is normally Windows-specific. The full Bethesda game-export path requires a compatible working toolchain.

```sh
python3.11 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
python launcher.py
pytest -q
```

## Test status and limits

- Source unit/integration tests run with mock FaceFX and xWMA tool processes plus actual FFmpeg. They validate container structure, paths, collision rules, saved project records, and older regression tests.
- **Not yet Windows GUI-tested** in this development environment (PyQt6 unavailable here).
- **Not yet tested with real Bethesda LIP generation, real xWMA on Windows, or in Fallout 4 / Skyrim.** Valid FUZ structure is not proof of successful in-game playback/lip animation.
- No Creation Kit record is written, generated, parsed or reconfigured. Mod authors remain responsible for their own dialogue plugin records and matching filenames.
- Existing upstream Chatterbox audio watermarking is unchanged.

## Licensing

See `LICENSE`, `THIRD_PARTY_NOTICES.md` and `BETHESDA_VOICE_EXPORT_RESEARCH.md`. User-provided game tooling has its own license terms.

## Startup regression protection and old EXE warnings

The v0.2.0 executable crashes at startup with `NameError: name 'host' is not defined`
inside the Export Library. v0.2.4 uses `self.host.player.stop`, and adds a Qt
**main-window and About-dialog smoke test** to `scripts/build_windows.ps1`. The installer
is blocked if the packaged GUI fails to initialize or About cannot be opened and reopened. Both the application icon
and the large Help/About logo are included in the PyInstaller asset list.

**IMPORTANT: Source updates do not modify a previously frozen `.exe`.** Build
from a fresh extraction of THIS v0.2.4 ZIP, then launch specifically
`dist\PlaguesVoiceStudio024\PlaguesVoiceStudio024.exe` or install the newly
created `PlaguesVoiceStudio024-Setup-0.2.4.exe`. Do not start an old desktop
shortcut that points at `PlaguedVoiceStudio020.exe`.

The frozen GUI smoke test report is `build\frozen-ui-smoke-test.json`.
Its `status` must be `passed` and `version` must be `0.2.4`.
No Windows executable or installer is included in this SOURCE archive.

## About dialog and virtual-memory diagnostics

The About button now uses a persistent non-modal dialog with logo and credits.
The packaged GUI self-test opens, closes, and reopens that dialog. An error
containing Windows OS 1455 is reported with paging-file recovery guidance.
See `RELEASE_NOTES_0.2.4.md`. Windows model loading still requires adequate
virtual memory; a successful packaging smoke test does not guarantee it.

## Build a GUI-only update without re-downloading model files

The normal Windows build command downloads only model sets you request, unless `-SkipModels` is provided.
If all model folders are already populated **in the current source directory**, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -FullOffline -SkipModels
```

`-SkipModels` does not copy models from another version's directory. Copy legitimate locally stored model directories into the new project's `models\` folder first, or let the script download them. The frozen test must pass before the installer is produced.
