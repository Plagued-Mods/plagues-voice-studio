"""Unit/integration tests with fake LIP/xWMA tools, no Bethesda assets needed."""
from pathlib import Path
import struct
import sys
import wave
import pytest
from chatterbox_studio.bethesda_export import (
    BethesdaExportError, BethesdaExportSettings, clean_transcript, export_dialogue,
    read_fuz, safe_segment, write_fuz,
)


def test_clean_transcript():
    assert clean_transcript("[narration] Hello, [chuckle] there. [pause:700ms] [rate:0.8]Stay.[/rate]") == "Hello, there. Stay."


def test_fuz_roundtrip(tmp_path, xwma_bytes):
    p = tmp_path / "voice.fuz"
    audio = xwma_bytes()
    lip = b"FAKE_LIP_BYTES"
    write_fuz(p, audio, lip)
    assert read_fuz(p) == (1, lip, audio)
    assert p.stat().st_size == 12 + len(lip) + len(audio)


def test_fuz_rejects_wrong_audio(tmp_path):
    with pytest.raises(BethesdaExportError, match="RIFF/xWMA"):
        write_fuz(tmp_path / "wrong.fuz", b"MP3_NOT_XWMA", b"LIP")


def test_file_validation():
    with pytest.raises(BethesdaExportError):
        safe_segment("../../Evil", "response")
    assert safe_segment("000F1B2C_1", "response") == "000F1B2C_1"


def _make_executable(path: Path, contents: str) -> None:
    path.write_text("#!/usr/bin/env python3\n" + contents, encoding="utf-8")
    path.chmod(0o755)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX test fake executable; Windows supports real .exe")
def test_mod_export_with_mock_tools(tmp_path, xwma_bytes):
    """Uses real FFmpeg + synthetic WAV, but no copyrighted external programs."""
    import imageio_ffmpeg
    _ = imageio_ffmpeg.get_ffmpeg_exe()
    wav = tmp_path / "spoken.wav"
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(b"\x00\x00" * 44100)
    fonix = tmp_path / "FonixData.cdf"
    fonix.write_bytes(b"stub for test")
    facefx = tmp_path / "FaceFXWrapper"
    _make_executable(facefx, """import sys\nfrom pathlib import Path\nassert sys.argv[1] in ('Fallout4', 'Skyrim')\nassert sys.argv[2] == 'USEnglish'\nassert 'Hello there.' == sys.argv[-1]\nPath(sys.argv[-2]).write_bytes(b'LIP_UNIT_TEST')\n""")
    encoder = tmp_path / "WMAEncodeRS"
    _make_executable(encoder, "import sys\nfrom pathlib import Path\nassert '--xwma' in sys.argv\nassert '-b' in sys.argv\n" +
                     f"Path(sys.argv[2]).write_bytes({xwma_bytes()!r})\n")
    root = tmp_path / "Game" / "Data"
    root.mkdir(parents=True)
    source_files = tmp_path / "source_files"
    source_files.mkdir()
    config = BethesdaExportSettings(
        source_audio=str(wav), text="[narration] Hello there. [chuckle]",
        game="fallout4", plugin_name="MyMod.esp", voice_type="MyNPCVoice", response_filename="000F1B2C_1",
        output_root=str(root), facefx_path=str(facefx), fonix_path=str(fonix), encoder_path=str(encoder),
        sidecar_root=str(source_files), destination_mode="game_data",
    )
    result = export_dialogue(config)
    assert result.is_file()
    assert result.parent == root / "Sound" / "Voice" / "MyMod.esp" / "MyNPCVoice"
    assert read_fuz(result)[1] == b"LIP_UNIT_TEST"
    assert (source_files / "MyMod.esp" / "MyNPCVoice" / "000F1B2C_1.wav").is_file()
    with pytest.raises(BethesdaExportError, match="Output exists"):
        export_dialogue(config)
    from dataclasses import replace
    replacement = export_dialogue(replace(config, overwrite_existing=True))
    assert replacement == result
    backups = list((source_files / "MyMod.esp" / "MyNPCVoice" / "backups").glob('*.fuz.bak'))
    assert len(backups) == 1
    assert read_fuz(backups[0])[1] == b'LIP_UNIT_TEST' 


def test_pcm_wav_not_accepted_as_xwm(tmp_path):
    from chatterbox_studio.bethesda_export import is_xwma
    wav = tmp_path / "voice.wav"
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(b"\x00\x00" * 200)
    assert not is_xwma(wav.read_bytes())
