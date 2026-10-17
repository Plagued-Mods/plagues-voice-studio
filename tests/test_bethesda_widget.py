"""Exercise actual Qt handoffs and project switching without model inference."""
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PyQt6.QtWidgets')
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QPlainTextEdit, QTabWidget
from chatterbox_studio.bethesda_widget import BethesdaExportTab
from chatterbox_studio.engine_lab import EngineLab
from chatterbox_studio.export_browser import ExportBrowser


@pytest.fixture(scope='module')
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def host(tmp_path, qt_app):
    window = QWidget()
    window.storage = tmp_path / 'data'
    window.storage.mkdir()
    window.settings = QSettings(str(tmp_path / 'settings.ini'), QSettings.Format.IniFormat)
    window.thread = None
    window.queue = []
    window.results = {}
    window._log = lambda *_: None
    window.voice = QComboBox(window)
    window.voice.addItem('Default', '')
    window.voice.addItem('Saved voice', 'saved-id')
    window.model = QComboBox(window)
    window.model.addItem('Nano', 'nano')
    window.editor = QPlainTextEdit(window)
    window.tabs = QTabWidget(window)
    window.bethesda_tab = BethesdaExportTab(window)
    window.tabs.addTab(window.bethesda_tab, 'Bethesda')
    yield window
    window.close()
    window.deleteLater()
    qt_app.processEvents()


@pytest.mark.parametrize('sender', [EngineLab.send_to_bethesda, ExportBrowser.send_selected])
def test_audio_handoff_loads_its_own_script(host, tmp_path, sender):
    recording = tmp_path / 'new recording.wav'
    recording.write_bytes(b'audio placeholder')
    recording.with_suffix('.json').write_text(json.dumps({
        'text': 'This is the generated dialogue.', 'ref_text': 'Entirely different speaker reference.'}))
    host.bethesda_tab.transcript.setPlainText('Previous recording, wrong dialogue.')
    sender(SimpleNamespace(host=host, selected_path=lambda: recording))
    assert host.bethesda_tab.audio.text() == str(recording)
    assert host.bethesda_tab.transcript.toPlainText() == 'This is the generated dialogue.'


@pytest.mark.parametrize('metadata', [None, b'broken JSON', b'[]', b'{"ref_text":"reference only"}', b'\xff'])
def test_old_or_unreadable_metadata_clears_stale_script(host, tmp_path, metadata):
    recording = tmp_path / 'old recording.wav'
    recording.write_bytes(b'audio placeholder')
    if metadata is not None:
        recording.with_suffix('.json').write_bytes(metadata)
    host.bethesda_tab.transcript.setPlainText('Stale dialogue must not survive an audio change.')
    host.bethesda_tab.audio.setText(str(recording))
    assert host.bethesda_tab.transcript.toPlainText() == ''


def test_chatterbox_handoff_uses_completed_job_snapshot(host, tmp_path):
    recording = tmp_path / 'narration.wav'
    recording.write_bytes(b'audio placeholder')
    host.queue = [SimpleNamespace(job_id='job1', text='Actual [chuckle] recorded words.')]
    host.results = {'job1': str(recording)}
    host.editor.setPlainText('An edited script that was never recorded.')
    host.bethesda_tab.audio.setText(str(recording))
    assert host.bethesda_tab.transcript.toPlainText() == 'Actual recorded words.'


def test_project_switch_does_not_reuse_other_projects_voicetype(host):
    tab = host.bethesda_tab
    first = tab.store.new_project('First mod', plugin='First.esp')
    voice = tab.store.new_voice('Actor', 'FirstVoice', 'saved-id', 'nano')
    first['voices'].append(voice)
    second = tab.store.new_project('Second mod', plugin='Second.esp')
    tab.projects = [first, second]
    tab._refresh_project_select(first['id'])
    tab._refresh_voice_select(voice['id'])
    assert tab.voice_type.text() == 'FirstVoice'
    tab.project_select.setCurrentIndex(tab.project_select.findData(second['id']))
    assert tab.plugin.text() == 'Second.esp'
    assert tab.voice_type.text() == ''


def test_saving_project_preserves_voicetype_being_entered(host):
    tab = host.bethesda_tab
    tab.project_name.setText('New mod')
    tab.plugin.setText('New.esp')
    tab.voice_type.setText('NewVoice')
    tab._save_project()
    assert tab.voice_type.text() == 'NewVoice'


def test_deleting_voice_assignment_clears_voicetype(host):
    tab = host.bethesda_tab
    project = tab.store.new_project('Mod')
    voice = tab.store.new_voice('Actor', 'ActorVoice', '', 'nano')
    project['voices'].append(voice)
    tab.projects = [project]
    tab._refresh_project_select(project['id'])
    tab._refresh_voice_select(voice['id'])
    tab._delete_voice_profile()
    assert tab.voice_type.text() == ''


def test_destination_preview_does_not_write_project_files(host):
    host.bethesda_tab._update_preview()
    assert not (host.storage / 'bethesda_source').exists()
    assert 'Incomplete destination' in host.bethesda_tab.preview.text()
