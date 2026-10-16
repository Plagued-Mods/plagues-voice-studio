# Plague's Voice Studio: Bethesda voice pipeline research

**Status:** Technical background from v0.1.4-preview, incorporated into the independently packaged v0.2.1 source. **Not yet verified in Fallout 4 or Skyrim inside the game.** For current installation paths and profile behavior see README.md.

## Confirmed architecture

1. The Chatterbox synthesis stage produces a WAV or MP3 master recording; it retains all existing narration functionality.
2. `Bethesda Voice Export` is an additional tab. It uses an *existing* recording and a plain spoken transcript with tags removed. It never re-renders the speech.
3. Prepares 16 kHz mono 16-bit PCM WAV for FaceFXWrapper, then passes the game's **own LIP profile**. FO4 uses `Fallout4`, Skyrim and Skyrim SE use `Skyrim`.
4. Prepares 44.1 kHz mono 16-bit PCM WAV for xWMA encoding. Uses a user-supplied `xwmaencode.exe` or the MIT `WMAEncodeRS.exe`. The latter is recommended for redistribution planning, but is *not bundled* here.
5. Packs the `.fuz` in our own audited Python code. Its format is `FUZE` + little-endian uint32 version (1) + uint32 lip size + LIP bytes + encoded audio bytes. Round-trip unpacking verifies our output.
6. Creates `Data/Sound/Voice/<YourMod.esp>/<VoiceType>/<ResponseFilename>.fuz` in a staging directory. Source WAV/LIP/XWM and transcript are kept separately in `PVS_Source_Files/` if requested. Do not include this backup directory in your shipped mod.

**Naming caveat:** Actual dialogue filenames must match Creation Kit dialogue response exports exactly. The UI lets users enter the filename but cannot derive it reliably without the plugin and CK-export metadata. Existing files are not overwritten.

## Tools and licensing

| Part | Candidate | Redistribution decision |
| --- | --- | --- |
| Audio preprocessing | FFmpeg via existing `imageio-ffmpeg` | Included in existing dependency; preserve applicable FFmpeg and build licensing notices |
| XWM encoder | https://github.com/MSIVST/WMAEncodeRS | MIT Rust source; encodes RIFF/xWMA with Windows codecs; check license notice and Windows Media runtime conditions before bundling the compiled EXE |
| Alternative XWM | xwmaencode.exe supplied by Bethesda Creation Kit | User installs official CK; **do not redistribute Bethesda's tool without permission** |
| LIP generation | https://github.com/Nukem9/FaceFXWrapper | Source repository is MIT-labelled but explicitly includes/depends on CK-derived material and Fonix data, covered by Bethesda licensing. **User-supplied binary only** pending license review |
| Fonix | `FonixData.cdf` from installed CK | Bethesda data; **never bundle** |
| FUZ | Local `bethesda_export.py` | Native Python packing, no external binary needed |
| Experimental alternative LIP | https://github.com/OpenFaceFX/OpenFaceFX | MIT clean-room Skyrim writer, but **not yet in-game verified**; FO4 LIP unsupported; do not market as production ready |
| Official FO4 alternative | Creation Kit `-GenerateLips:<Plugin>` | FO4 August 18, 2026 CK patch fixed command-line LipGen; plugin-level batch workflow should be a later integration path |

A game-independent approach isn't correct: Fallout 4 `.lip` differs from Skyrim `.lip` (see xVASynth `.lip`/`.fuz` plugin documentation).

## Known constraints and validation plan

- The preview was tested with **synthetic stand-in tools** and structural FUZ round-trip tests. A passing mock encoder proves packaging code, **not in-game compatibility**.
- xWMA must be real RIFF/xWMA data, not MP3 or plain WAV with a changed extension. Source audio remains archival; the encoded XWM and lip data are packaged for the game.
- The transcript should reflect *actual spoken words* including any unexpected model deviations. Nonverbal utterances can affect synchrony.
- `FaceFXWrapper` may fail on particular Creation Kit builds; use its 6-argument (already resampled WAV) mode. Capture errors and leave no false `.fuz` successes.
- A user should produce a 1–2 sentence test in each game: verify audible dialogue, mouth animation, subtitle alignment, playback length, and proper archive deployment. Repeat with a different NPC voice type.
- Batch metadata import from CK and automated creation of game plugins/BA2 archives are not part of this preview.
- This feature requires working external Windows tools and has **not** been tested on Windows in this environment.
- Fallout 4's August 2026 CK patch mentions FUZ with embedded WAV for **PlayStation Creations**; do not assume that allowance applies to standard PC xWMA workflows.

## Documentation / sources reviewed

- https://github.com/Nukem9/FaceFXWrapper
- https://github.com/MSIVST/WMAEncodeRS
- https://github.com/OpenFaceFX/OpenFaceFX
- https://openfacefx.com/docs/COMPATIBILITY/
- https://openfacefx.com/docs/api/exporters/
- https://www.nexusmods.com/skyrimspecialedition/mods/55605
- https://help.bethesda.net/app/answers/detail/a_id/72995/
- https://github.com/RLR64/Robo-Voice-Pipeline
- https://github.com/charlestietjen/fallout4-revoiced-tool

## Next release milestones

1. Test **actual Windows FaceFXWrapper + FonixData + xWMA** on FO4 and SSE voice sample quests; capture reference fixture FUZ files.
2. Import CK-exported dialogue metadata for correct FormID/Response/VoiceType filenames, batch manifest and automatic queue creation.
3. Expose optional official CK `-GenerateLips:` fallback for supported versions; implement test discovery and caching to avoid reencoding unchanged dialogue.
4. Package Windows distribution only after full third-party license audit and side-by-side game tests.
