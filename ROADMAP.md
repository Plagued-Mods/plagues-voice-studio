# Plague's Voice Studio — Project Roadmap

## Future goal: Live voice-generation demo on the Plagued Mods website

**Status:** Deferred for future development. Not implemented or deployed.

Visitors should eventually be able to try a restricted version of Plague's Voice Studio from its product page without installing the desktop application.

### Planned user experience

- Enter a short original sample text (approximately 200–300 characters).
- Choose from a small set of pre-approved demonstration voices.
- Choose a supported engine available on the demo server (Chatterbox and/or Qwen3-TTS).
- Generate speech, listen to it, and follow the desktop application download link.
- Preserve the existing Plagued Mods design and accessibility practices.

### Implementation and safety requirements

- Keep the static website separate from a secured Python inference API.
- Run inference only on a dedicated, provisioned backend. Never expose a desktop installation or its control endpoints directly to the public Internet.
- Enforce request-size limits, per-client rate limits, a concurrency/queue limit, temporary audio retention and automatic cleanup.
- Use server-controlled reference voices only at launch; require explicit speaker permission and avoid anonymous uploads.
- Protect the API against arbitrary command execution and untrusted filesystem paths.
- Consider user-visible usage limits and queue wait times, particularly for CPU inference.
- Verify backend resources, model terms, abuse controls and hosting cost before deployment.
- Do not imply the browser runs the Windows PyQt6 GUI or can access the visitor's local models.

**Open hosting decision:** Existing Hostinger VPS suitability versus dedicated inference host versus a securely tunneled private test machine. No provider or hardware has been selected.

### Acceptance criteria

The production page demonstrates **real** locally hosted synthesis, limits abuse and costs, works on mobile, and clearly labels the engine and origin of playback. The desktop app remains a separate download.

## Near-term goal: Genuine downloadable voice samples

Before building the live inference service, publish short, consent-cleared audio samples from working desktop installations. Keep original WAV recordings and note engine/model, language, voice permissions, and software version. The website can publish compressed MP3 copies for accessible playback.

See [samples/README.md](samples/README.md).

## Release notes

The creator has confirmed working Windows speech generation with Chatterbox, Qwen3-TTS and IndexTTS 2.5. The roadmap focuses on future features, not whether IndexTTS already functions in the desktop application.
