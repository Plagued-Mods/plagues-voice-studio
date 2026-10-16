"""Local voice reference library. Files are copied, never linked to sources."""
from __future__ import annotations
import json
import shutil
import wave
from pathlib import Path
from uuid import uuid4


class VoiceLibrary:
    def __init__(self, root: Path, *, read_only: bool = False):
        self.root = Path(root)
        self.audio_dir = self.root / 'voices'
        self.index = self.root / 'voices.json'
        self.read_only = read_only
        if not read_only:
            self.audio_dir.mkdir(parents=True, exist_ok=True)

    def list_voices(self) -> list[dict]:
        if not self.index.is_file():
            return []
        try:
            items = json.loads(self.index.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return []
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict) and
                (self.audio_dir / str(item.get("file", ""))).is_file()]

    def import_voice(self, name: str, source: Path) -> dict:
        if self.read_only:
            raise ValueError('This voice library is read-only')
        name = name.strip()
        source = Path(source)
        if not name or len(name) > 80:
            raise ValueError("Voice name must be 1–80 characters")
        if source.suffix.lower() not in (".wav", ".flac", ".ogg", ".mp3"):
            raise ValueError("Use a WAV, FLAC, OGG or MP3 reference")
        if not source.is_file():
            raise ValueError("Reference audio was not found")
        # sf.info handles the supported formats that the installed libsndfile can decode.
        import soundfile as sf
        try:
            info = sf.info(str(source))
        except Exception as exc:
            raise ValueError(f"Unable to decode reference audio: {exc}") from exc
        if info.duration <= 5.0:
            raise ValueError("Reference voice must be longer than five seconds")
        if info.duration > 120.0:
            raise ValueError("Reference voice must be at most two minutes; trim it first")
        if info.channels > 2:
            raise ValueError("Reference audio must be mono or stereo")
        if any(v['name'].casefold() == name.casefold() for v in self.list_voices()):
            raise ValueError("A voice with that name already exists")
        filename = uuid4().hex + source.suffix.lower()
        destination = self.audio_dir / filename
        shutil.copy2(source, destination)
        item = {"id": uuid4().hex, "name": name, "file": filename,
                "duration": round(info.duration, 1)}
        try:
            self._store(self.list_voices() + [item])
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return item

    def remove_voice(self, voice_id: str) -> bool:
        if self.read_only:
            raise ValueError('This voice library is read-only')
        items = self.list_voices()
        matched = [v for v in items if v['id'] == voice_id]
        if not matched:
            return False
        self._store([v for v in items if v['id'] != voice_id])
        (self.audio_dir / matched[0]['file']).unlink(missing_ok=True)
        return True

    def resolve(self, voice_id: str) -> str:
        for voice in self.list_voices():
            if voice['id'] == voice_id:
                return str(self.audio_dir / voice['file'])
        return ""

    def _store(self, items: list[dict]) -> None:
        if self.read_only:
            raise ValueError('This voice library is read-only')
        temporary = self.index.with_suffix('.tmp')
        temporary.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.index)
