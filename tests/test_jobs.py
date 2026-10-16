from pathlib import Path
import pytest
from chatterbox_studio.jobs import NarrationJob
from chatterbox_studio.engine import unique_output_path


def make_job(**replacements):
    base = dict(text='Hello world.', model='english', device='cpu', language='en',
                voice_path='', output_path='output.wav', format='wav')
    base.update(replacements)
    return NarrationJob(**base)


def test_validation():
    make_job().validate()
    with pytest.raises(ValueError, match='reference voice'):
        make_job(model='turbo').validate()
    make_job(model='nano').validate()
    with pytest.raises(ValueError, match='match'):
        make_job(output_path='output.mp3').validate()
    with pytest.raises(ValueError, match='Unsupported language'):
        make_job(model='multilingual-v3', language='xyz').validate()


def test_unique_output(tmp_path):
    start = tmp_path / 'one.wav'
    start.write_bytes(b'old')
    (tmp_path / 'one_2.wav').write_bytes(b'old2')
    assert unique_output_path(start) == tmp_path / 'one_3.wav'
