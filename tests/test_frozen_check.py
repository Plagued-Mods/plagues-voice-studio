"""Regression checks for the requests metadata issue in a frozen EXE."""
from pathlib import Path
from chatterbox_studio import frozen_check


def test_required_metadata_includes_requests():
    assert 'requests' in frozen_check.REQUIRED_METADATA
    assert 'transformers' in frozen_check.REQUIRED_METADATA


def test_report_fails_on_missing_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(frozen_check, 'check_metadata',
                        lambda: ({'torch': '2.6.0'}, ['Missing distribution metadata: requests']))
    monkeypatch.setattr(frozen_check, 'check_runtime_imports',
                        lambda: (_ for _ in ()).throw(AssertionError('Do not import on missing metadata')))
    report = tmp_path / 'report.json'
    assert frozen_check.run(report) == 1
    assert 'requests' in report.read_text()


def test_report_passes_on_success(tmp_path, monkeypatch):
    monkeypatch.setattr(frozen_check, 'check_metadata', lambda: ({'requests': '2.34.2'}, []))
    monkeypatch.setattr(frozen_check, 'check_runtime_imports', lambda: [])
    report = tmp_path / 'report.json'
    assert frozen_check.run(report) == 0
    assert '"status": "passed"' in report.read_text()


def test_spec_explicitly_collects_metadata():
    spec = (Path(__file__).resolve().parents[1] / 'ChatterboxStudio.spec').read_text()
    assert "'requests'" in spec
    assert 'datas += copy_metadata(package)' in spec
