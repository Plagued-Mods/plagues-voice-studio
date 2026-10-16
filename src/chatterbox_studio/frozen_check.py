"""Check a frozen Windows build BEFORE producing an installer.

Launch using `PlaguesVoiceStudio030Experimental.exe --self-test report.json`. This does not
load model weights or synthesize speech, and can run without internet. A
nonzero exit code means the binary is not ready to distribute.
"""
from __future__ import annotations
import importlib.metadata
import json
import traceback
from pathlib import Path

# Keep synchronized with ChatterboxStudio.spec. This covers the dependency
# versions queried by Transformers and the core speech/audio stack.
REQUIRED_METADATA = (
    "requests", "regex", "filelock", "fsspec", "huggingface-hub",
    "tokenizers", "safetensors", "packaging", "numpy", "PyYAML",
    "tqdm", "transformers", "torch", "torchaudio", "chatterbox-tts",
    "plagues-voice-studio-v030", "diffusers", "librosa", "soundfile",
    "imageio-ffmpeg", "s3tokenizer", "resemble-perth",
)


def check_metadata():
    versions, errors = {}, []
    for distribution in REQUIRED_METADATA:
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"Missing distribution metadata: {distribution}")
    return versions, errors


def check_runtime_imports():
    errors = []
    try:
        import transformers  # noqa: F401 - deliberately triggers its metadata validation
        from chatterbox.tts_turbo import ChatterboxTurboTTS  # noqa: F401
        from chatterbox.tts import ChatterboxTTS  # noqa: F401
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS  # noqa: F401
    except Exception:
        errors.append("Runtime model import failed:\n" + traceback.format_exc())
    return errors


def run(report_path: Path | None = None) -> int:
    versions, errors = check_metadata()
    if not errors:
        errors.extend(check_runtime_imports())
    result = {"status": "failed" if errors else "passed", "versions": versions, "errors": errors}
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 1 if errors else 0
