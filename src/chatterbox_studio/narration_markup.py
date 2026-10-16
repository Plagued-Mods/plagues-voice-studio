"""Safe, deterministic local narration directives for Plague's Voice Studio.

These are APPLICATION directives, not special tokens of Chatterbox.
The original Chatterbox brackets (e.g. [laugh]) are preserved verbatim.
"""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RenderStep:
    kind: str  # speech | pause
    text: str = ""
    pause_ms: int = 0
    rate: float = 1.0
    volume: float = 1.0
    emphasis: bool = False


_TAG = re.compile(r"\[([^\[\]\n\r]+)\]")
_PAUSE = re.compile(r"pause\s*:\s*(\d+(?:\.\d+)?)\s*(ms|s)", re.I)
_NUMERIC = re.compile(r"(rate|volume)\s*:\s*(\d+(?:\.\d+)?)", re.I)
_END = re.compile(r"/(rate|volume|emphasis)", re.I)
_NEW = re.compile(r"(?:pause|rate|volume|emphasis)(?:\s*:.*)?$", re.I)
_RESERVED = re.compile(r"/?(?:pause|rate|volume|emphasis)(?=\s|:|$)", re.I)


class MarkupError(ValueError):
    """Readable narration mark-up error, with a source-line reference."""


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def parse_script(text: str) -> list[RenderStep]:
    """Turn styled passages and pauses into safe render steps; do not interpret native tags.

    Supports properly nested, non-overlapping [rate:X]...[/rate],
    [volume:X]...[/volume], [emphasis]...[/emphasis],
    and [pause:0.8s] or [pause:800ms] directives.
    """
    result: list[RenderStep] = []
    values = {"rate": 1.0, "volume": 1.0, "emphasis": False}
    stack: list[tuple[str, float | bool]] = []
    buffer = ""

    def flush():
        nonlocal buffer
        if buffer.strip():
            result.append(RenderStep("speech", text=buffer.strip(),
                                     rate=float(values["rate"]),
                                     volume=float(values["volume"]),
                                     emphasis=bool(values["emphasis"])))
        buffer = ""

    position = 0
    for match in _TAG.finditer(text):
        buffer += text[position:match.start()]
        tag = match.group(1).strip()
        normalized = tag.lower()
        source_line = _line(text, match.start())
        pause = _PAUSE.fullmatch(tag)
        numeric = _NUMERIC.fullmatch(tag)
        closing = _END.fullmatch(tag)
        if pause:
            ms = float(pause.group(1)) * (1000 if pause.group(2).lower() == 's' else 1)
            if not 0 <= ms <= 10000:
                raise MarkupError(f"Line {source_line}: pause must be from 0 to 10 seconds")
            flush()
            result.append(RenderStep("pause", pause_ms=round(ms)))
        elif numeric:
            key = numeric.group(1).lower()
            val = float(numeric.group(2))
            minimum, maximum = (0.5, 2.0) if key == 'rate' else (0.0, 2.0)
            if not minimum <= val <= maximum:
                raise MarkupError(f"Line {source_line}: {key} must be {minimum} to {maximum}")
            if any(k == key for k, _ in stack):
                raise MarkupError(f"Line {source_line}: nested {key} scopes are not supported")
            flush()
            stack.append((key, values[key]))
            values[key] = val
        elif normalized == 'emphasis':
            if any(k == 'emphasis' for k, _ in stack):
                raise MarkupError(f"Line {source_line}: nested emphasis scopes are not supported")
            flush()
            stack.append(('emphasis', values['emphasis']))
            values['emphasis'] = True
        elif closing:
            key = closing.group(1).lower()
            if not stack or stack[-1][0] != key:
                raise MarkupError(f"Line {source_line}: unmatched or out-of-order [/{key}]")
            flush()
            _, previous = stack.pop()
            values[key] = previous
        elif _RESERVED.match(tag):
            raise MarkupError(f"Line {source_line}: invalid directive [{tag}]. See Narration Tags help.")
        else:
            # Native Chatterbox tags, such as [laugh], must remain unmodified.
            buffer += match.group(0)
        position = match.end()

    buffer += text[position:]
    flush()
    if stack:
        raise MarkupError("Unclosed directive(s): " + ', '.join('[' + key + ']' for key, _ in stack))
    if not any(s.kind == 'speech' for s in result):
        raise MarkupError("The script needs some spoken text")
    return result


def plan_script(text: str, max_chars: int, default_gap_ms: int) -> list[RenderStep]:
    """Split styled passages into manageable chunks and insert default inter-chunk gaps.

    Explicit pause replaces, rather than adds to, the default segment gap.
    """
    from .text_split import split_script
    expanded: list[RenderStep] = []
    for step in parse_script(text):
        if step.kind == 'pause':
            expanded.append(step)
        else:
            for part in split_script(step.text, max_chars):
                expanded.append(RenderStep("speech", text=part, rate=step.rate,
                                           volume=step.volume, emphasis=step.emphasis))
    output: list[RenderStep] = []
    for index, step in enumerate(expanded):
        if (step.kind == 'speech' and output and output[-1].kind == 'speech'
                and default_gap_ms):
            output.append(RenderStep('pause', pause_ms=default_gap_ms))
        if step.kind == 'pause' and output and output[-1].kind == 'pause':
            last = output.pop()
            output.append(RenderStep('pause', pause_ms=last.pause_ms + step.pause_ms))
        else:
            output.append(step)
    return output
