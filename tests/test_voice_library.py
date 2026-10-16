from pathlib import Path
import wave
import pytest
import numpy as np
from chatterbox_studio.voices import VoiceLibrary


def create_voice(path: Path, duration=6.0):
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes((np.zeros(int(8000*duration), dtype=np.int16)).tobytes())


def test_voice_import_remove(tmp_path):
    original = tmp_path / 'original.wav'
    create_voice(original)
    lib = VoiceLibrary(tmp_path / 'state')
    result = lib.import_voice('Narrator', original)
    original.unlink()
    assert len(lib.list_voices()) == 1
    assert Path(lib.resolve(result['id'])).is_file()
    with pytest.raises(ValueError, match='already exists'):
        lib.import_voice('narrator', Path(lib.resolve(result['id'])))
    assert lib.remove_voice(result['id'])
    assert lib.list_voices() == []


def test_reject_short_voice(tmp_path):
    file = tmp_path / 'short.wav'
    create_voice(file, 4.0)
    with pytest.raises(ValueError, match='five seconds'):
        VoiceLibrary(tmp_path / 'voice_dir').import_voice('test', file)
