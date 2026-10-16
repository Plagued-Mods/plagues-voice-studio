"""Isolated v0.2 library with read-only access to the user's v0.1.x voices.

Never writes to or removes any file belonging to the older application.
"""
from __future__ import annotations
from pathlib import Path
import os
import re
import sys
from datetime import datetime
from .voices import VoiceLibrary


def legacy_data_dir() -> Path:
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local'))) / 'ChatterboxStudio'
    return Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share'))) / 'ChatterboxStudio'


def old_export_directories() -> list[Path]:
    return [Path.home() / 'Music' / 'Chatterbox Studio', legacy_data_dir() / 'exports']


def new_export_directory(storage: Path) -> Path:
    music = Path.home() / 'Music'
    return music / "Plague's Voice Studio 0.2" if music.is_dir() else storage / 'exports'


def safe_voice_name(name: str) -> str:
    """Conservative file stem, based on the user's selected voice display name."""
    name = re.sub(r'[^A-Za-z0-9_-]+', '_', name.strip())
    return name.strip('_-')[:64] or 'default'


def narration_basename(voice_name: str | None, at: datetime | None = None) -> str:
    at = at or datetime.now()
    prefix = safe_voice_name(voice_name or 'default')
    return f'{prefix}_narration_{at:%Y%m%d-%H%M%S}'


class CompatibleVoiceLibrary:
    """Local writable library + older read-only voice references.

    Legacy identifiers are prefixed to avoid accidental conflicts. New imports
    are always written to v0.2 storage. Removal of old voices is prohibited.
    """
    def __init__(self, storage: Path):
        self.current = VoiceLibrary(storage)
        # Read metadata and reference paths without touching legacy storage.
        old = legacy_data_dir()
        self.legacy = VoiceLibrary(old, read_only=True) if old.is_dir() else None

    def list_voices(self) -> list[dict]:
        current = self.current.list_voices()
        previous = [dict(item, id='legacy:' + item['id'], name=item['name'] + ' (v0.1.x)')
                    for item in (self.legacy.list_voices() if self.legacy else [])]
        return current + previous

    def resolve(self, voice_id: str) -> str:
        if voice_id.startswith('legacy:'):
            return self.legacy.resolve(voice_id[7:]) if self.legacy else ""
        return self.current.resolve(voice_id)

    def import_voice(self, name: str, source: Path) -> dict:
        return self.current.import_voice(name, source)

    def remove_voice(self, voice_id: str) -> bool:
        if voice_id.startswith('legacy:'):
            raise ValueError('This voice belongs to v0.1.x and is read-only. Import a copy into v0.2 to manage it.')
        return self.current.remove_voice(voice_id)
