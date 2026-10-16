# Plague's Voice Studio — Genuine Audio Samples

This directory defines the demonstration scripts and their provenance. **No generated recordings are bundled here yet.** The build environment used to prepare this documentation has no Chatterbox or Qwen3 model weights and cannot download them. We will never pass off operating-system TTS or unrelated synthesized speech as a Plague's Voice Studio engine sample.

## Suggested recordings

Generate these short original passages in a working installation, then export a WAV (and, optionally, create an MP3 copy for website playback):

| Proposed filename | Engine / model | Language | Exact spoken text |
| --- | --- | --- | --- |
| `chatterbox-turbo-narration.wav` | Chatterbox Turbo | English | "Every story deserves a voice. From a quiet whisper to a thunderous announcement, Plague's Voice Studio puts creative narration in your hands." |
| `qwen3-06b-voice-clone.wav` | Qwen3-TTS 0.6B Base | English | "One voice, countless possibilities. Create, listen, and refine your spoken performances locally with Plague's Voice Studio." |
| `qwen3-06b-spanish.wav` | Qwen3-TTS 0.6B Base | Spanish | "Cada historia merece una voz propia. Con Plague's Voice Studio, puedes crear narraciones y dar vida a tus personajes." |

The supplied prose is example narration; it is not evidence of any speech engine's output. Use only owned or permitted reference voices; avoid unverified claims about model quality or timbre. Do not record the same reference voice in another language without checking whether that model supports it appropriately.

## Production checklist

1. Generate on the current desktop build and listen for errors.
2. Record the actual engine, model identifier, language, CPU/GPU used and software version.
3. Keep the unmodified WAV as the original; use FFmpeg or similar only to produce a web-friendly MP3 derivative.
4. Save the audio files under `samples/audio/` and document permissions for each voice. Never include personally sensitive reference clips.
5. Copy approved MP3 derivatives to `assets/audio/voice-studio/` in the *separate Plagued Mods website project* and update that site's `samples.json` manifest.
6. Confirm browsers play the samples and verify the file attribution. Do not publish empty audio links.

The website showcase is designed to hide audio-player controls until its audio manifest includes real published files. The live text-to-speech website demo is a separate future milestone documented in [ROADMAP.md](../ROADMAP.md).
