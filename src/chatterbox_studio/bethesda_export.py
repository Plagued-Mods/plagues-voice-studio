"""Bethesda dialogue voice exports, independent of Chatterbox inference.

This module deliberately does NOT contain Creation Kit code, FonixData.cdf,
FaceFXWrapper, or a proprietary xWMA encoder. The user supplies their own
legally installed FaceFX-compatible tool and xWMA encoder. The FUZE container
writer is a clean Python implementation of the public container format.

Supported target game choices produce distinct LIP types; each must be checked
in-game by the user. Ordinary WAV/MP3 narration exports are unaffected.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Callable
import json
import os
import re
import shutil
import struct
import subprocess
import wave


class BethesdaExportError(RuntimeError):
    """Actionable failure in export prerequisites or tool execution."""


GAMES = {"fallout4": "Fallout4", "skyrim": "Skyrim", "skyrimse": "Skyrim"}
ENCODERS = {"xwmaencode", "wmaencoders"}
FUZ_MAGIC = b"FUZE"
# Chatterbox marker tags are not dialogue words. Also remove PVS markup.
_TAG = re.compile(r"\[[^\[\]\r\n]*\]")
_SPACE = re.compile(r"\s+")
_BAD_SEGMENT = re.compile(r"[\\/\x00-\x1f<>:\"|?*]")
_RESERVED_SEGMENT = re.compile(r"^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", re.I)


def clean_transcript(script: str) -> str:
    """Remove all bracketed synthesis directives from the dialogue transcript.

    The transcript must still be reviewed against the recorded audio, because
    a script's punctuation, pronunciation or spoken reactions may differ.
    """
    return _SPACE.sub(" ", _TAG.sub(" ", script)).strip()


def safe_segment(text: str, label: str) -> str:
    part = _BAD_SEGMENT.sub("_", text).strip(" .")
    if not part or part != text or _RESERVED_SEGMENT.match(part):
        raise BethesdaExportError(f"Enter a valid {label} without path separators or special characters")
    if len(part) > 120:
        raise BethesdaExportError(f"{label} is too long")
    return part


def is_xwma(data: bytes) -> bool:
    """Check RIFF bounds, WMA format, seek table and nonempty packet data.

    This validates the container, not the compressed audio's audible content.
    A RIFF/XWMA label alone does not establish that encoding succeeded.
    """
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] not in (b"XWMA", b"WAVE"):
        return False
    if struct.unpack_from("<I", data, 4)[0] + 8 != len(data):
        return False
    pos = 12
    chunks = {}
    while pos + 8 <= len(data):
        tag = data[pos:pos+4]
        size = struct.unpack_from("<I", data, pos+4)[0]
        start = pos + 8
        end = start + size
        pos = end + size % 2
        if pos > len(data):
            return False
        if tag in (b"fmt ", b"dpds", b"data"):
            if tag in chunks:
                return False
            chunks[tag] = data[start:end]
    if pos != len(data) or any(tag not in chunks for tag in (b"fmt ", b"dpds", b"data")):
        return False
    fmt, seek, packets = (chunks[tag] for tag in (b"fmt ", b"dpds", b"data"))
    if len(fmt) < 18 or not seek or len(seek) % 4 or not packets:
        return False
    codec, channels, rate, avg_bytes, block_align, bits, extra = struct.unpack_from("<HHIIHHH", fmt)
    # XAudio2 accepts WMA2 and WMA3. PCM (1) is never xWMA.
    if codec not in (0x0161, 0x0162) or not all((channels, rate, avg_bytes, block_align)):
        return False
    if len(fmt) < 18 + extra or bits != 16:
        return False
    previous = 0
    for (decoded_bytes,) in struct.iter_unpack("<I", seek):
        if decoded_bytes < previous or decoded_bytes % (channels * 2):
            return False
        previous = decoded_bytes
    return previous > 0


def write_fuz(path: Path, xwm: bytes, lip: bytes, *, version: int = 1) -> None:
    """Write a Bethesda FUZE container: header, LIP length/data, xWMA audio.

    This is packaging, not lip synthesis or xWMA encoding. Require plausible
    real xWMA and LIP data so a WAV mistakenly renamed XWM is rejected.
    """
    if not lip:
        raise BethesdaExportError("A non-empty LIP file is required for dialogue")
    if not is_xwma(xwm):
        raise BethesdaExportError("The encoder did not produce RIFF/xWMA audio")
    if version != 1 or len(lip) > 0xFFFFFFFF:
        raise BethesdaExportError("Invalid FUZ header values")
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".partial")
    try:
        with partial.open("wb") as fh:
            fh.write(FUZ_MAGIC)
            fh.write(struct.pack("<II", version, len(lip)))
            fh.write(lip)
            fh.write(xwm)
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)


def read_fuz(path: Path) -> tuple[int, bytes, bytes]:
    contents = path.read_bytes()
    if len(contents) < 12 or contents[:4] != FUZ_MAGIC:
        raise BethesdaExportError("Not a complete FUZE container")
    version, size = struct.unpack_from("<II", contents, 4)
    if size > len(contents) - 12:
        raise BethesdaExportError("LIP length exceeds FUZ file size")
    lip, xwm = contents[12:12+size], contents[12+size:]
    if version != 1 or not lip or not is_xwma(xwm):
        raise BethesdaExportError("FUZ must contain version 1, non-empty LIP and complete RIFF/xWMA audio")
    return version, lip, xwm


def audio_transcript(path: Path) -> str:
    """Read the output script, never the reference speaker's transcript.

    Older recordings may have no script metadata. Return empty text so the UI
    asks for the matching dialogue rather than retaining another line's script.
    """
    try:
        metadata = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    except (OSError, ValueError, UnicodeError):
        return ''
    text = metadata.get('text') if isinstance(metadata, dict) else None
    return clean_transcript(text) if isinstance(text, str) else ''


def _tool(path: str, label: str) -> str:
    path = path.strip().strip('"')
    if not path:
        raise BethesdaExportError(f"Select the {label} executable in the Bethesda Export tab")
    candidate = Path(path).expanduser()
    if candidate.is_file():
        return str(candidate.resolve())
    found = shutil.which(path)
    if found:
        return found
    raise BethesdaExportError(f"Cannot find {label}: {path}")


def _call(args: list[str], action: str) -> None:
    try:
        kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
        result = subprocess.run(args, capture_output=True, text=True, errors="replace", timeout=240, **kwargs)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise BethesdaExportError(f"{action} could not run: {e}") from e
    if result.returncode:
        details = (result.stderr or result.stdout or "No error text").strip()
        raise BethesdaExportError(f"{action} failed (exit {result.returncode}): {details[-1000:]}")


@dataclass(frozen=True)
class BethesdaExportSettings:
    source_audio: str
    text: str
    game: str
    plugin_name: str
    voice_type: str
    response_filename: str
    output_root: str
    facefx_path: str
    fonix_path: str
    encoder_path: str
    encoder_type: str = "wmaencoders"  # MIT Rust WMAEncodeRS, or CK xwmaencode
    bitrate_kbps: int = 48
    keep_intermediate: bool = True
    ffmpeg_path: str = ""
    destination_mode: str = "game_data"  # game_data or mod_root
    overwrite_existing: bool = False
    sidecar_root: str = ""  # separate project files from installed Game Data

    def validate(self) -> None:
        if self.game not in GAMES:
            raise BethesdaExportError("Choose Fallout 4, Skyrim, or Skyrim SE")
        if not Path(self.source_audio).is_file():
            raise BethesdaExportError("Select a WAV or MP3 file that already exists")
        if not clean_transcript(self.text):
            raise BethesdaExportError("Dialogue text is required for lip synchronization")
        for value, label in ((self.plugin_name, "plugin filename"), (self.voice_type, "voice type")):
            safe_segment(value, label)
        response_stem(self.response_filename)
        if Path(self.plugin_name).suffix.lower() not in {".esp", ".esm", ".esl"}:
            raise BethesdaExportError("Plugin filename must end in .esp, .esm, or .esl")
        if self.encoder_type not in ENCODERS:
            raise BethesdaExportError("Choose a supported encoder type")
        if self.bitrate_kbps not in (32, 48):
            raise BethesdaExportError("For 44.1 kHz mono speech, select 32 or 48 kbps")
        if not Path(self.fonix_path).is_file():
            raise BethesdaExportError("Select FonixData.cdf from your locally installed Creation Kit")
        _tool(self.facefx_path, "FaceFXWrapper")
        _tool(self.encoder_path, "xWMA encoder")
        if self.ffmpeg_path:
            _tool(self.ffmpeg_path, "FFmpeg")
        if not self.output_root.strip():
            raise BethesdaExportError("Choose an output directory")
        if self.destination_mode not in ("game_data", "mod_root"):
            raise BethesdaExportError("Choose a supported installation target")
        if not Path(self.output_root).expanduser().is_dir():
            raise BethesdaExportError("Installation root must be an existing folder")
        if self.destination_mode == "game_data" and Path(self.output_root).name.casefold() != "data":
            raise BethesdaExportError("Game Data mode requires the actual game Data directory")
        if self.destination_mode == "mod_root" and Path(self.output_root).name.casefold() == "data":
            raise BethesdaExportError("MO2 mod mode requires the mod root, NOT a Data directory")
        if self.sidecar_root and not Path(self.sidecar_root).is_dir():
            raise BethesdaExportError("Source files directory must exist")


def _ffmpeg_path(setting: BethesdaExportSettings) -> str:
    if setting.ffmpeg_path:
        return _tool(setting.ffmpeg_path, "FFmpeg")
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError) as exc:
        raise BethesdaExportError("FFmpeg is required; install imageio-ffmpeg or choose its executable") from exc


def response_stem(filename: str) -> str:
    """Accept a CK basename (optionally with audio extension), never a path."""
    value = filename.strip()
    if not value or '/' in value or '\\' in value or value in ('.', '..'):
        raise BethesdaExportError('Supply the exact dialogue filename without any folder path')
    part = Path(value)
    if part.suffix and part.suffix.lower() not in ('.fuz', '.wav', '.lip', '.xwm'):
        raise BethesdaExportError('Response filename must have no extension or a voice-file extension')
    return safe_segment(part.stem if part.suffix else value, 'response filename')


def expected_fuz_path(setting: BethesdaExportSettings) -> Path:
    """Preview exact deploy path without invoking external tools.

    Root is either the game's existing Data/ folder or the root of a mod manager's
    mod folder. Both have Sound/Voice directly underneath, never Data/Data.
    """
    if not setting.output_root.strip():
        raise BethesdaExportError("Choose an output directory")
    root = Path(setting.output_root).expanduser().resolve()
    plugin = safe_segment(setting.plugin_name, "plugin filename")
    voice = safe_segment(setting.voice_type, "voice type")
    stem = response_stem(setting.response_filename)
    if not stem:
        raise BethesdaExportError("Enter an exact dialogue response filename")
    return root / "Sound" / "Voice" / plugin / voice / (stem + ".fuz")


def _check_prepared_wav(path: Path, rate: int) -> None:
    try:
        with wave.open(str(path), 'rb') as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) != (1, 2, rate):
                raise BethesdaExportError(f"Audio preparation must produce {rate} Hz, 16-bit mono PCM")
            if audio.getnframes() == 0 or not audio.readframes(1):
                raise BethesdaExportError("Audio preparation produced an empty recording")
    except (OSError, EOFError, wave.Error) as exc:
        raise BethesdaExportError(f"Audio preparation did not produce a readable PCM WAV: {exc}") from exc


def export_dialogue(setting: BethesdaExportSettings, report: Callable[[str], None] = lambda _: None) -> Path:
    """Prepare dialogue using external tools, then deploy an atomic FUZ file.

    No ESP/ESM/ESL is parsed or modified. Caller supplies the precise expected
    response filename. Existing FUZ requires explicit overwrite permission and
    a separate backup; intermediates remain outside the game/mod folder.
    """
    setting.validate()
    fuz_path = expected_fuz_path(setting)
    stem = fuz_path.stem
    plugin, voice = fuz_path.parent.parent.name, fuz_path.parent.name
    if fuz_path.exists() and not setting.overwrite_existing:
        raise BethesdaExportError(f"Output exists; approval required before replacing: {fuz_path}")
    # Deployable folders must contain only game assets, not debug source files.
    base = Path(setting.sidecar_root).expanduser().resolve() if setting.sidecar_root else Path(setting.source_audio).resolve().parent / 'PVS_Source_Files'
    sidecar_dir = base / plugin / voice
    ffmpeg = _ffmpeg_path(setting)
    facefx = _tool(setting.facefx_path, "FaceFXWrapper")
    encoder = _tool(setting.encoder_path, "xWMA encoder")

    with TemporaryDirectory(prefix="pvs_bethesda_") as tmp:
        scratch = Path(tmp)
        speech_wav = scratch / "lipsync_16khz.wav"
        encoding_wav = scratch / "encoding_44khz.wav"
        lip_file = scratch / (stem + ".lip")
        xwm_file = scratch / (stem + ".xwm")
        report("Resampling for lip sync (16 kHz, 16-bit mono)...")
        _call([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", setting.source_audio,
               "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(speech_wav)], "LIP audio preparation")
        _check_prepared_wav(speech_wav, 16000)
        report("Generating game-specific LIP animation...")
        # The documented 6-argument FaceFXWrapper form accepts a pre-resampled WAV.
        _call([facefx, GAMES[setting.game], "USEnglish", setting.fonix_path,
               str(speech_wav), str(lip_file), clean_transcript(setting.text)], "FaceFX LIP generation")
        if not lip_file.is_file() or lip_file.stat().st_size == 0:
            raise BethesdaExportError("FaceFX returned success but did not produce a LIP file")

        report("Resampling engine audio (44.1 kHz, 16-bit mono)...")
        _call([ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", setting.source_audio,
               "-vn", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(encoding_wav)], "XWM audio preparation")
        _check_prepared_wav(encoding_wav, 44100)
        report("Encoding xWMA audio...")
        if setting.encoder_type == "wmaencoders":
            _call([encoder, str(encoding_wav), str(xwm_file), "--xwma",
                   "-b", str(setting.bitrate_kbps)], "WMAEncodeRS encoding")
        else:
            _call([encoder, "-b", str(setting.bitrate_kbps * 1000),
                   str(encoding_wav), str(xwm_file)], "Creation Kit xwmaencode encoding")
        if not xwm_file.is_file() or xwm_file.stat().st_size < 12:
            raise BethesdaExportError("Encoder returned success but did not produce XWM audio")

        report("Packing Bethesda FUZ container...")
        lip_data, xwm_data = lip_file.read_bytes(), xwm_file.read_bytes()
        # Reject broken tool output before replacing any retained source files.
        candidate = scratch / 'candidate.fuz'
        write_fuz(candidate, xwm_data, lip_data)
        version, verified_lip, verified_xwm = read_fuz(candidate)
        if version != 1 or verified_lip != lip_data or verified_xwm != xwm_data:
            raise BethesdaExportError("FUZ round-trip validation failed")
        if setting.keep_intermediate:
            sidecar_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(encoding_wav, sidecar_dir / (stem + ".wav"))
            shutil.copy2(lip_file, sidecar_dir / (stem + ".lip"))
            shutil.copy2(xwm_file, sidecar_dir / (stem + ".xwm"))
            (sidecar_dir / (stem + ".txt")).write_text(clean_transcript(setting.text), encoding="utf-8")
        fuz_path.parent.mkdir(parents=True, exist_ok=True)
        if fuz_path.exists():
            if not setting.overwrite_existing:
                raise BethesdaExportError(f"Target exists: {fuz_path}")
            backup_root = sidecar_dir / 'backups'
            backup_root.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            backup = backup_root / f'{stem}-{timestamp}.fuz.bak'
            shutil.copy2(fuz_path, backup)
            report(f"Backed up previous FUZ to: {backup}")
        # Separate application instances must not share the same partial file.
        with NamedTemporaryFile(prefix=fuz_path.name + '.', suffix='.pvs-partial',
                                dir=fuz_path.parent, delete=False) as staged:
            deploy_tmp = Path(staged.name)
        try:
            shutil.copy2(candidate, deploy_tmp)
            if setting.overwrite_existing:
                os.replace(deploy_tmp, fuz_path)
            elif os.name == 'nt':
                # Windows rename refuses to replace an existing target, even
                # one created after the earlier existence check.
                os.rename(deploy_tmp, fuz_path)
            else:
                # POSIX rename replaces; link provides exclusive publication
                # of the already complete file on the same filesystem.
                os.link(deploy_tmp, fuz_path)
        except FileExistsError as exc:
            raise BethesdaExportError(f"Target appeared during export; existing file was preserved: {fuz_path}") from exc
        finally:
            deploy_tmp.unlink(missing_ok=True)
        if fuz_path.stat().st_size != candidate.stat().st_size:
            raise BethesdaExportError("Installed FUZ size mismatch")
        report(f"Voice package ready: {fuz_path}")
        return fuz_path
