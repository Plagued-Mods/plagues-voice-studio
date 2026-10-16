"""Writable per-user files and read-only packaged models."""
import os
import sys
from pathlib import Path


def user_data_dir() -> Path:
    override = os.environ.get("PLAGUES_VOICE_STUDIO_030_HOME")
    if override:
        root = Path(override).expanduser()
    elif sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "PlaguesVoiceStudio-v030-Experimental"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "PlaguesVoiceStudio-v030-Experimental"
    root.mkdir(parents=True, exist_ok=True)
    return root


def bundled_models_dir() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base / "models"
