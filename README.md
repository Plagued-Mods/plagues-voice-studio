# Plague's Voice Studio v0.3.0-alpha4, EXPERIMENTAL

**Created by Kaotick Jay.** Local voice production for narration, radio and game dialogue.

This is an **experimental, standalone branch** built from the v0.2.4 stable source. Do not overwrite or uninstall v0.2.4. The preserved stable archive has SHA-256 `23464fb7c541e000d03f2c47f14e18629fe70d97f1b9b4d4ebadf556776d5928`.


## Alpha 4: Optional engine diagnostics and unblocked GUI

- No pop-up command prompt when launching optional Qwen / Index Python on Windows.
- On-screen engine stages, elapsed clock, persistent diagnostic logs, and Cancel.
- Logs saved in the **experimental** AppData folder under `engine_logs`.
- Model-download and CPU loading can still be slow. The new generation limit is 45 minutes.
- Existing engine environments and model weights are not changed.

**Already have an alpha3 build?** Apply the alpha4 patch to that directory, then run
`powershell -ExecutionPolicy Bypass -File .\REBUILD_ALPHA4_EXISTING.ps1`. It reuses
`.venv-build` without pip-installing or recompressing a distribution archive.
The Windows executable still requires validation with real Qwen model weights.

## Alpha 3: External Python import-path isolation

**Fix for** `ImportError: Module use of python311.dll conflicts with this version of Python`.

Resetting the Windows DLL search path alone is insufficient because running
`<external-python> <bundled>/_internal/optional_engine_runner.py` prepends the
script directory to the external interpreter's `sys.path`. That directory
contains PyInstaller's Python 3.11 native extension modules. Alpha 3 adds
`-I` to the Python command for **both** engine probing and WAV generation;
this enables isolated mode and prevents automatic insertion of the script
directory while still allowing imports from the optional engine's venv.

First validate an installed Qwen3 runtime **outside** Voice Studio:

```powershell
$qwen = Join-Path $env:LOCALAPPDATA 'PlaguesVoiceStudio-v030-Experimental\engines\qwen3\Scripts\python.exe'
& $qwen -I .\optional_engine_runner.py --probe qwen3
```

Expected result is a final JSON object with `"ready": true`; warnings about
FlashAttention or SoX are separate issues. You must rebuild the EXE after
updating the launcher. This change does not reinstall models or dependencies.

## Alpha 2 Windows compatibility fix

Qwen3-TTS and IndexTTS run in external Python environments. Alpha 2 prevents the bundled Python 3.11 app from leaking its DLL search path into Python 3.12 optional-engine subprocesses. Rebuild the Windows EXE after updating the source. No optional-engine reinstall or model re-download is needed.

## Added in the experimental branch

- **Optional Engine Lab**, with adapters for Qwen3-TTS Base 0.6B/1.7B and IndexTTS 2.5.
- Independent per-engine Python interpreters. Neither optional engine is installed or loaded by the Chatterbox host at startup.
- **Named character profiles** with per-engine model/language/device settings and shared reference voice. Saved to experimental-only JSON.
- **A/B comparison**, rendering the same passage with both configured optional engines sequentially; measured rendering time, WAV outputs, playback and integration with the existing Bethesda exporter.
- **Separate app identity**, settings, installation, user data and export folder. Existing v0.2.x and v0.1.x voice references can be selected read-only.
- Process cancellation, JSON sidecar metadata and built-in configuration/probe validation.

**Scope:** These optional adapters have not been tested with real weights on the user's Windows/AMD hardware. The unit tests validate the protocol with a mock subprocess. The Windows executable and live model inference must be built/tested locally. CPU speech generation may be extremely slow or unsupported by an upstream engine. Neither optional library nor its weights are redistributed by this source package.

Read **[OPTIONAL_ENGINES.md](OPTIONAL_ENGINES.md)** before setting up extra models. It includes the official upstream links, Windows installation scripts and license warnings.

## Existing features retained

- Chatterbox Nano, Turbo, Original English and Multilingual V3, unchanged Narration Studio generation pipeline.
- Source text import/export, markup (`[pause]`, `[rate]`, `[volume]`, `[emphasis]`) in Chatterbox narration, WAV/MP3, batch queue.
- Persistent saved voice references and an Export Library with playback of older recordings.
- Bethesda project mappings, WAV/LIP/XWM/FUZ production, and optional direct game/mod installation using locally supplied conversion tools. Game plugin files are never edited.
- Dark-green branded PyQt6 GUI, searchable Help center, About/Credits/Diagnostics, and Windows frozen runtime & Qt smoke tests.

## Separate environments and data

| | Stable v0.2.4 | Experimental v0.3.0 |
|---|---|---|
| Executable | `PlaguesVoiceStudio024.exe` | `PlaguesVoiceStudio030Experimental.exe` |
| Data | `%LOCALAPPDATA%\PlaguesVoiceStudio-v021` | `%LOCALAPPDATA%\PlaguesVoiceStudio-v030-Experimental` |
| Settings | `KaotickJay/PlaguesVoiceStudio021` | `KaotickJay/PlaguesVoiceStudio030Experimental` |
| Windows installation | Stable app folder | `Plague's Voice Studio 0.3 Experimental` |
| Voices | Writable stable v0.2.x | New imports writable; stable v0.2.x and v0.1.x read-only |
| Models | Chatterbox | Same Chatterbox core, optional Qwen/Index in separate Python processes |

Stable Bethesda project profiles are **not automatically imported**, preventing modifications to the stable data store. Recreate experimental mappings or manually back up/import compatible profiles only after verifying them.

## Building on Windows

Windows x64, Python 3.11, Git, internet for initial Chatterbox installation and model acquisition. Inno Setup 6 is optional.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -Models turbo
```

The result is `dist\PlaguesVoiceStudio030Experimental\PlaguesVoiceStudio030Experimental.exe` after successful frozen metadata and GUI smoke tests. For bundling all **four Chatterbox models**, use `-FullOffline`; this does **not** install Qwen3-TTS or IndexTTS. If all models are already in the new source's `models\` directory, add `-SkipModels` to avoid downloading again.

To preview source UI with an already prepared `.venv-build` environment, run `PREVIEW_GUI.bat`. A source-code change does not update an existing EXE; rebuilding is required.

The optional Qwen and Index runtimes are installed separately **only if you decide to do so**, following `OPTIONAL_ENGINES.md`. Use **Optional Engine Lab → Test selected engine** before generating anything. Model weight downloads may be large.

## Testing status

The Python source and protocol are unit-tested in a Linux container without PyQt6 or model weights. This does **not** establish Windows GUI, AMD GPU, optional-model inference, or Bethesda in-game compatibility. The Windows build uses a frozen Qt smoke test which must pass before installers are emitted.

## Licensing

MIT applies to original project code subject to the included `LICENSE`. Chatterbox is by Resemble AI. PyQt6 and optional engines have their own licenses. In particular, IndexTTS 2.5 uses a **Bilibili Model Use License Agreement**. No optional engine weights, model code or vendor binaries are bundled. See `THIRD_PARTY_NOTICES.md` and upstream model cards before redistributing a bundle.
