from datetime import datetime
from pathlib import Path
from dataclasses import replace
import json
import pytest
from chatterbox_studio.mod_profiles import ModProfileStore, ProfileError
from chatterbox_studio.pvs_library import narration_basename, safe_voice_name
from chatterbox_studio.bethesda_export import BethesdaExportSettings, BethesdaExportError, expected_fuz_path, response_stem


def test_export_name_by_voice():
    dt = datetime(2026, 10, 15, 17, 48, 12)
    assert narration_basename('Hattie "Mama Mire" Boggs', dt) == 'Hattie_Mama_Mire_Boggs_narration_20261015-174812'
    assert narration_basename(None, dt) == 'default_narration_20261015-174812'
    assert safe_voice_name('../../') == 'default'


def test_profiles_are_separately_stored(tmp_path):
    store = ModProfileStore(tmp_path / 'v020')
    project = store.new_project('Companion', plugin='Companion.esp', game='fallout4', root='C:/Fallout4/Data')
    voice = store.new_voice('Companion Voice', 'MyCompanionVoice', 'legacy:voice-id', 'turbo')
    project['voices'].append(voice)
    store.save([project])
    assert store.load() == [project]
    assert store.path == tmp_path / 'v020' / 'bethesda_profiles.json'
    assert not (tmp_path / 'ChatterboxStudio').exists()
    store.path.write_text('invalid json')
    with pytest.raises(ProfileError):
        store.load()


def test_direct_game_data_and_mo2_paths(tmp_path):
    base = tmp_path / 'Fallout4' / 'Data'
    base.mkdir(parents=True)
    config = BethesdaExportSettings(
        source_audio='', text='', game='fallout4', plugin_name='My Mod.esp',
        voice_type='MyNPCVoice', response_filename='000F1B2C_1.fuz',
        output_root=str(base), facefx_path='', fonix_path='', encoder_path='')
    path = expected_fuz_path(config)
    assert path == base / 'Sound' / 'Voice' / 'My Mod.esp' / 'MyNPCVoice' / '000F1B2C_1.fuz'
    assert 'Data/Data' not in str(path)
    mo2 = tmp_path / 'MO2' / 'mods' / 'Companion'
    mo2.mkdir(parents=True)
    mod_config = replace(config, output_root=str(mo2), destination_mode='mod_root')
    assert expected_fuz_path(mod_config) == mo2 / 'Sound' / 'Voice' / 'My Mod.esp' / 'MyNPCVoice' / '000F1B2C_1.fuz'
    # No attempt is made to open/edit My Mod.esp or infer the owning INFO record.
    assert not (mo2 / 'My Mod.esp').exists()


def test_missing_filename_rejected(tmp_path):
    c = BethesdaExportSettings(source_audio='', text='', game='fallout4', plugin_name='X.esp',
         voice_type='V', response_filename='', output_root=str(tmp_path),
         facefx_path='', fonix_path='', encoder_path='')
    with pytest.raises(BethesdaExportError):
        expected_fuz_path(c)


def test_response_filename_traversal_and_extensions():
    for value in ('../00000001_1', '..\\00000001_1', 'foo.txt', '', '.'):
        with pytest.raises(BethesdaExportError):
            response_stem(value)
    assert response_stem('00000123_1.fuz') == '00000123_1'
    assert response_stem('00000123_1') == '00000123_1'
