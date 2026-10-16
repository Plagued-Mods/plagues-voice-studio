"""Split long scripts conservatively into manageable Chatterbox prompts."""
from __future__ import annotations
import re

_SENTENCE_END = re.compile(r'(?<=[.!?。！？])\s+(?=[^\s])')


def _cut_words(text: str, limit: int) -> list[str]:
    """Split a single too-long sentence on word boundaries; hard-cut as last resort."""
    result: list[str] = []
    words = text.split()
    current = ""
    for word in words:
        if len(word) > limit:
            if current:
                result.append(current)
                current = ""
            result.extend(word[pos:pos + limit] for pos in range(0, len(word), limit))
        elif not current:
            current = word
        elif len(current) + 1 + len(word) <= limit:
            current += " " + word
        else:
            result.append(current)
            current = word
    if current:
        result.append(current)
    return result


def split_script(text: str, max_chars: int = 220) -> list[str]:
    """Retain order and punctuation; preferentially split paragraphs/sentences.

    This is a character budget, not a tokenizer guarantee. Shorter chunks reduce
    runaway speech and allow cancellation, but may affect natural transitions.
    """
    if not 60 <= max_chars <= 2000:
        raise ValueError("Chunk length must be between 60 and 2000 characters")
    text = text.strip()
    if not text:
        return []
    segments = []
    for paragraph in re.split(r'\n\s*\n|\n', text):
        paragraph = " ".join(paragraph.split())
        if not paragraph:
            continue
        sentences = _SENTENCE_END.split(paragraph)
        current = ""
        for sentence in sentences:
            for part in ([sentence] if len(sentence) <= max_chars else _cut_words(sentence, max_chars)):
                if not current:
                    current = part
                elif len(current) + 1 + len(part) <= max_chars:
                    current += " " + part
                else:
                    segments.append(current)
                    current = part
        if current:
            segments.append(current)
    return segments
