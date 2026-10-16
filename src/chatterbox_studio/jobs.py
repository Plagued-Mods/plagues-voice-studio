"""Serializable narration job snapshots."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from uuid import uuid4

MODEL_CHOICES = {
    "nano": "Nano, efficient English (CPU friendly)",
    "turbo": "Turbo, expressive English",
    "english": "Original English, creative controls",
    "multilingual-v3": "Multilingual V3, 23 languages",
}
LANGUAGES = {
    "ar": "Arabic", "da": "Danish", "de": "German", "el": "Greek",
    "en": "English", "es": "Spanish", "fi": "Finnish", "fr": "French",
    "he": "Hebrew", "hi": "Hindi", "it": "Italian", "ja": "Japanese",
    "ko": "Korean", "ms": "Malay", "nl": "Dutch", "no": "Norwegian",
    "pl": "Polish", "pt": "Portuguese", "ru": "Russian", "sv": "Swedish",
    "sw": "Swahili", "tr": "Turkish", "zh": "Chinese",
}

@dataclass(frozen=True)
class NarrationJob:
    text: str
    model: str
    device: str
    language: str
    voice_path: str
    output_path: str
    format: str = "wav"
    max_chars: int = 220
    pause_ms: int = 180
    exaggeration: float = 0.5
    cfg_weight: float = 0.5
    temperature: float = 0.8
    job_id: str = ""

    def validate(self) -> None:
        from .narration_markup import parse_script
        if not self.text.strip():
            raise ValueError("Enter some narration text")
        if self.model not in MODEL_CHOICES:
            raise ValueError("Unknown Chatterbox model")
        if self.device not in ("auto", "cpu", "cuda"):
            raise ValueError("Unknown processing device")
        if self.model == "multilingual-v3" and self.language not in LANGUAGES:
            raise ValueError("Unsupported language")
        if self.model == "turbo" and not self.voice_path:
            raise ValueError("Turbo requires an imported reference voice")
        if self.voice_path and not Path(self.voice_path).is_file():
            raise ValueError("The selected voice file no longer exists")
        if self.format not in ("wav", "mp3"):
            raise ValueError("Only WAV and MP3 exports are supported")
        if Path(self.output_path).suffix.lower() != f".{self.format}":
            raise ValueError("Output filename does not match the selected format")
        if not 60 <= self.max_chars <= 2000:
            raise ValueError("Chunk length must be 60–2000 characters")
        if not 0 <= self.pause_ms <= 2500:
            raise ValueError("Pause must be between 0 and 2500 ms")
        if not 0 <= self.exaggeration <= 1 or not 0 <= self.cfg_weight <= 1:
            raise ValueError("Expressiveness controls must be between 0 and 1")
        if not 0.1 <= self.temperature <= 1.5:
            raise ValueError("Temperature must be 0.1–1.5")
        parse_script(self.text)

    def as_json(self) -> dict:
        return asdict(self)

    @classmethod
    def new(cls, **kwargs):
        return cls(job_id=uuid4().hex, **kwargs)
