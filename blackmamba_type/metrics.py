from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(frozen=True)
class MetricsSnapshot:
    words: int
    characters: int
    elapsed_seconds: float
    wpm: float
    chars_per_second: float
    saved_keystrokes: int
    accepted_completions: int


class SessionMetrics:
    def __init__(self) -> None:
        self._started = time.monotonic()
        self._text = ""
        self._saved_keystrokes = 0
        self._accepted_completions = 0

    def observe_text(self, text: str) -> None:
        self._text = text

    def record_completion(self, prefix: str, completion: str, saved: int) -> None:
        self._saved_keystrokes += max(0, int(saved))
        self._accepted_completions += 1

    def reset(self, text: str = "") -> None:
        self._started = time.monotonic()
        self._text = text
        self._saved_keystrokes = 0
        self._accepted_completions = 0

    def snapshot(self) -> MetricsSnapshot:
        elapsed = max(time.monotonic() - self._started, 0.001)
        chars = len(self._text)
        words = len(self._text.split())
        minutes = elapsed / 60.0
        # Conventional approximation: five characters ~= one word.
        wpm = (chars / 5.0) / minutes if minutes > 0 else 0.0
        cps = chars / elapsed
        return MetricsSnapshot(
            words=words,
            characters=chars,
            elapsed_seconds=elapsed,
            wpm=wpm,
            chars_per_second=cps,
            saved_keystrokes=self._saved_keystrokes,
            accepted_completions=self._accepted_completions,
        )
