from pathlib import Path
import numpy as np
import soundfile as sf
import pytest
from chatterbox_studio.jobs import NarrationJob
from chatterbox_studio.engine import Engine, GenerationCancelled


class FakeModel:
    sr = 8000
    conds = object()
    def __init__(self):
        self.calls = []
    def prepare_conditionals(self, path, exaggeration=0.5):
        self.conds = object()
    def generate(self, text, **options):
        self.calls.append((text, options))
        return np.zeros((1, 800), dtype=np.float32)


def job(tmp_path, **options):
    d = dict(text=('Hello world. ' * 40), model='english', device='cpu', language='en',
             voice_path='', output_path=str(tmp_path / 'export.wav'),
             max_chars=85, pause_ms=100, format='wav')
    d.update(options)
    return NarrationJob(**d)


def test_render_and_chunk_progress(tmp_path):
    model = FakeModel()
    progress = []
    result = Engine(model_loader=lambda *_: model).render(
        job(tmp_path), lambda msg: None, lambda n, total: progress.append((n, total)), lambda: False)
    assert result.exists()
    assert len(model.calls) > 1
    assert progress[-1][0] == progress[-1][1]
    samples, sr = sf.read(result)
    assert sr == 8000
    assert len(samples) == len(model.calls) * 800 + (len(model.calls) - 1) * 800
    assert Engine(model_loader=lambda *_: model).render(job(tmp_path), lambda _: None,
           lambda *_: None, lambda: False).stem.endswith('_2')


def test_cancel_removes_partial(tmp_path):
    model = FakeModel()
    e = Engine(model_loader=lambda *_: model)
    with pytest.raises(GenerationCancelled):
        e.render(job(tmp_path), lambda _: None, lambda *_: None,
                 lambda: len(model.calls) >= 1)
    assert not list(tmp_path.glob('*.partial.wav'))
    assert not list(tmp_path.glob('*.wav'))
