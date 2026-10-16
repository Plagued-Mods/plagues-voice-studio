"""Saved Bethesda project + voice profiles, entirely separate from the old app."""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
import json
import os


class ProfileError(ValueError):
    pass


class ModProfileStore:
    def __init__(self, storage: Path):
        self.path = Path(storage) / 'bethesda_profiles.json'

    def load(self) -> list[dict]:
        if not self.path.is_file():
            return []
        try:
            value = json.loads(self.path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            raise ProfileError(f'Cannot read Bethesda profiles: {exc}') from exc
        if not isinstance(value, dict) or value.get('version') != 1 or not isinstance(value.get('projects'), list):
            raise ProfileError('Unknown Bethesda profile format; existing file was not changed')
        return value['projects']

    def save(self, projects: list[dict]) -> None:
        if not isinstance(projects, list):
            raise ProfileError('Project profiles must be a list')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix('.json.tmp')
        try:
            with tmp.open('w', encoding='utf-8') as f:
                json.dump({'version': 1, 'projects': projects}, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        finally:
            tmp.unlink(missing_ok=True)

    @staticmethod
    def new_project(name: str, **fields) -> dict:
        if not name.strip():
            raise ProfileError('Project name is required')
        return {'id': uuid4().hex, 'name': name.strip(), 'voices': [], **fields}

    @staticmethod
    def new_voice(name: str, voice_type: str, voice_id: str, model: str) -> dict:
        if not name.strip() or not voice_type.strip():
            raise ProfileError('Voice profile name and Creation Kit voice type are required')
        return {'id': uuid4().hex, 'name': name.strip(), 'voice_type': voice_type.strip(),
                'voice_id': voice_id, 'model': model}
