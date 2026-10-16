# Speech engines: supported Qwen3-TTS and experimental IndexTTS 2.5

**Baseline:** Plague's Voice Studio v0.2.4 remains unchanged. The separate v0.3.0-alpha4 build retains the four Chatterbox models in **Narration Studio** and provides a working Qwen3-TTS implementation through the **Voice Engines** tab. IndexTTS 2.5 remains experimental. Keep independent engine runtimes out of `.venv-build` and the PyInstaller distribution folder.

## Engine status and requirements

| Adapter | Functional interface | Requirements | Verified here |
| --- | --- | --- | --- |
| Qwen3-TTS (supported) | 0.6B Base and 1.7B Base offered, reference-voice cloning, English and 9 other languages, WAV | Separate Python 3.12, `qwen-tts`, model weights (download on first use) | Successful Windows CPU synthesis and WAV output with real 0.6B Base weights; 1.7B not yet verified |
| IndexTTS 2.5 (experimental) | Reference-voice cloning, five languages, optional emotion vector, duration factor, WAV | Separate `uv` environment, official `index-tts` checkout and `checkpoints/` weights | Protocol unit tests only; installation and live speech generation not verified on Windows/AMD |

The application does not install these backends automatically. It launches an explicitly chosen Python interpreter as a local subprocess, using JSON input/output and no network server. Model downloads, if any, are done by the engine itself and may contact Hugging Face. An optional engine failure does **not** replace or uninstall Chatterbox. First-time model loading can be very slow on CPU.

The Windows graphics hardware compatibility of these engines, especially AMD Radeon and Windows 10, is **unverified**. Defaults prefer CPU and full precision where supported. NVIDIA CUDA requires an independently compatible installation. The app cannot guarantee that IndexTTS works on CPU for every upstream release.

## Installing Qwen3-TTS (separate from Chatterbox)

1. Review the official [Qwen3-TTS repository](https://github.com/QwenLM/Qwen3-TTS) and its licensing, install Python 3.12.
2. From the experimental source root, run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup_qwen_windows.ps1
   ```

3. In **Voice Engines**, point **Qwen3 Python** at the interpreter printed by the script, typically `%LOCALAPPDATA%\PlaguesVoiceStudio-v030-Experimental\engines\qwen3\Scripts\python.exe`.
4. Click **Save runtime paths**, choose Qwen3, then **Test selected engine**. This validates imports, not downloading weights or inferring real speech.
5. Select a model, your existing voice reference, a reference transcript if you have one, and a test script. Generate. The Base model can use an x-vector-only speaker embedding when the transcript is omitted, but providing an exact transcript may improve similarity.

## Installing IndexTTS 2.5 (independent repository/runtime)

1. Read the [IndexTTS repository](https://github.com/index-tts/index-tts), its `LICENSE` (Bilibili Model Use License Agreement) and `DISCLAIMER`. Do not assume commercial redistribution rights.
2. Install Git and [uv](https://docs.astral.sh/uv/).
3. From the experimental source root, after reviewing the license, run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\scripts\setup_index_windows.ps1 -LicenseReviewed -DownloadModels
   ```

4. In Engine Lab, set both the repository directory and the `.venv\Scripts\python.exe` created under it. Click **Save runtime paths**, then **Test selected engine**.
5. Choose a reference voice, a supported language (EN, ES, JA, ZH, AR) and emotion/duration controls. The 0.5–2.0 `duration_factor` applies to IndexTTS; **greater than 1 slows speech**, unlike ordinary speed multipliers.

For either engine, installing packages or weights may require significant free disk space and virtual memory. If a library has changed its Python API upstream, the optional runner may need adjustment. This source build does not bundle independent engine wheels or weights.

## Reusable characters and comparisons

1. In **Voice Engines**, choose or type a character name (e.g., `Hattie Mama Mire Boggs`). Choose the voice reference; the stable v0.2.x library is offered read-only.
2. Pick Qwen3, its model/language/device, then **Save profile**.
3. Pick IndexTTS, configure its model/language/emotion/duration, and **Save profile** again under the **same character name**. Per-engine settings are retained in the experimental `character_profiles.json`.
4. Paste the same test passage, then choose **Compare Engines** (experimental, requires IndexTTS). Results appear as individual WAVs with time measurements, descriptive filenames, and `.json` metadata. Play any result, browse it in the Export Library, or send it to the Bethesda LIP/XWM/FUZ workflow.
5. If you close the app during optional generation, it asks you to stop that work first. Cancel terminates the active engine child process. Comparisons render sequentially to limit peak memory demand.

**Important:** The Voice Engines workflow currently sends plain text directly to Qwen3 and IndexTTS. Chatterbox-specific `[pause:...]`, `[rate:...]` and vocal-event tokens are **not parsed or guaranteed** there. Use the stable Narration Studio to process those tags. No MP3 or persistent batch queue yet for optional engines. No claim of identical voice timbre or human-quality output across engines is made.

## Directory isolation

- Stable v0.2.x user data: `%LOCALAPPDATA%\PlaguesVoiceStudio-v021`, **read only** from experimental build.
- Experimental v0.3 user data: `%LOCALAPPDATA%\PlaguesVoiceStudio-v030-Experimental`.
- Experimental character presets: `character_profiles.json`, runtime interpreter settings: `optional_engines.json`.
- v0.1.x voices are also available read-only if present.
- Experimental exports: `Music\Plague's Voice Studio Experimental` when Music exists, otherwise the experimental user-data exports folder.
- Stable settings registry identifier: `PlaguesVoiceStudio021`, experimental: `PlaguesVoiceStudio030Experimental`.
- Existing v0.2.x Bethesda project profiles are deliberately **not modified or automatically migrated**. Create or copy mappings inside the experimental branch as needed; the stable database is untouched.

## Packaging and licensing

The experimental Windows build includes the optional runner script but **does not** bundle `qwen-tts`, `indextts`, or their model weights. The core `-FullOffline` build bundles the **four Chatterbox models only**. IndexTTS source and weights remain subject to their upstream Bilibili license, while Qwen3-TTS has separate code and model terms. PyQt6 remains subject to its GPL/commercial license. Respect speaker permission and avoid distributing third-party model assets without verifying the relevant licenses.

Before adopting a result into a production mod, compare the pronunciation, emotional delivery, consistency, artifacts, and inference time, and test any generated game-voice file in the game.

### Alpha4 diagnostics

For Qwen3-TTS use Voice Engines > Test selected engine, then Generate. Qwen3 0.6B Base inference is working on Windows CPU; IndexTTS remains experimental.
A live diagnostic pane shows model import, model loading, first-time download,
CPU inference and WAV-writing stages. An elapsed clock remains visible during
long CPU generation. Press Cancel if it stalls. Probe and generation logs
are stored in `%LOCALAPPDATA%\PlaguesVoiceStudio-v030-Experimental\engine_logs`.
The core executable does not show a Python command prompt on Windows.
First-time weights can be large and need disk space. A passing import probe
only checks the engine installation, not actual synthesis.
