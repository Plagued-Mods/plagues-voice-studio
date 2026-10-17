"""Script-preview regression tests without requiring a GUI environment."""
import json
from chatterbox_studio.export_metadata import read_export_script


def test_exact_script_roundtrip(tmp_path):
    sound = tmp_path / 'Mama_Mire.wav'
    text = '[narration] The river\u2019s quiet.\n\n[whispering] But not for long.  '
    sound.with_suffix('.json').write_text(json.dumps({'text': text, 'engine': 'chatterbox', 'model': 'turbo'}), encoding='utf-8')
    found, status = read_export_script(sound)
    assert found == text
    assert 'chatterbox' in status and 'turbo' in status


def test_optional_engine_sidecar_preview(tmp_path):
    sound = tmp_path / 'Qwen-001.wav'
    text = 'Buenos d\u00edas.\n[advertisement] Goodneighbor Records.'
    sound.with_suffix('.json').write_text(json.dumps({'engine': 'qwen3', 'text': text}), encoding='utf-8')
    assert read_export_script(sound)[0] == text


def test_missing_sidecar_avoids_stale_script(tmp_path):
    assert read_export_script(tmp_path / 'legacy.wav')[0] is None


def test_bad_metadata_is_handled(tmp_path):
    sound = tmp_path / 'bad.wav'
    meta = sound.with_suffix('.json')
    for value in ('bad-json', '[]', '{"text": null}', '{"text": "   "}'):
        meta.write_text(value, encoding='utf-8')
        script, status = read_export_script(sound)
        assert script is None
        assert status


def test_numbered_export_uses_matching_json(tmp_path):
    first = tmp_path / 'story.wav'
    second = tmp_path / 'story_2.wav'
    first.with_suffix('.json').write_text('{"text":"First recording"}', encoding='utf-8')
    second.with_suffix('.json').write_text('{"text":"Second recording"}', encoding='utf-8')
    assert read_export_script(first)[0] == 'First recording'
    assert read_export_script(second)[0] == 'Second recording'
