from __future__ import annotations

import json
import queue
import threading
from collections import Counter
from pathlib import Path
from typing import Iterable


def _normalize_word(word: str) -> str:
    value = (word or "").strip("'’-_ ").casefold()
    if len(value) < 2 or len(value) > 48:
        return ""
    if not any(ch.isalpha() for ch in value):
        return ""
    if any(ch.isdigit() for ch in value):
        return ""
    if not all(ch.isalpha() or ch in "'’-" for ch in value):
        return ""
    return value


def extract_words(text: str) -> list[str]:
    words: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        normalized = _normalize_word("".join(buffer))
        buffer.clear()
        if normalized:
            words.append(normalized)

    for ch in text or "":
        if ch.isalpha() or ch in "'’-":
            buffer.append(ch)
        else:
            flush()
    flush()
    return words


class PersonalLexicon:
    """Local frequency lexicon.

    Only normalized word frequencies are persisted. Raw keystrokes and full
    sentences are intentionally not stored.
    """

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (Path.home() / ".blackmamba_type" / "lexicon.json")
        self._counts: Counter[str] = Counter()
        self._lock = threading.RLock()
        self._dirty = 0
        self.load()

    def load(self) -> None:
        with self._lock:
            if not self.path.exists():
                return
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return

            counts = raw.get("words", {}) if isinstance(raw, dict) else {}
            if not isinstance(counts, dict):
                return

            clean: Counter[str] = Counter()
            for word, count in counts.items():
                normalized = _normalize_word(str(word))
                try:
                    number = int(count)
                except (TypeError, ValueError):
                    continue
                if normalized and number > 0:
                    clean[normalized] = number
            self._counts = clean
            self._dirty = 0

    def save(self) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "version": 1,
                "words": dict(self._counts.most_common()),
            }
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            tmp.replace(self.path)
            self._dirty = 0

    def record_word(self, word: str, amount: int = 1) -> bool:
        normalized = _normalize_word(word)
        if not normalized:
            return False
        with self._lock:
            self._counts[normalized] += max(1, int(amount))
            self._dirty += 1
            if self._dirty >= 20:
                self.save()
        return True

    def import_text(self, text: str) -> int:
        words = extract_words(text)
        if not words:
            return 0
        counts = Counter(words)
        with self._lock:
            self._counts.update(counts)
            self._dirty += len(words)
            self.save()
        return len(words)

    def suggest(self, prefix: str, limit: int = 12) -> list[tuple[str, int]]:
        p = _normalize_word(prefix)
        if not p:
            return []
        with self._lock:
            matches = [
                (word, count)
                for word, count in self._counts.items()
                if word.startswith(p)
            ]
        matches.sort(key=lambda item: (-item[1], len(item[0]), item[0]))
        return matches[: max(1, int(limit))]

    def frequency(self, word: str) -> int:
        normalized = _normalize_word(word)
        if not normalized:
            return 0
        with self._lock:
            return int(self._counts.get(normalized, 0))

    def unique_words(self) -> int:
        with self._lock:
            return len(self._counts)

    def total_words(self) -> int:
        with self._lock:
            return sum(self._counts.values())

    def clear(self) -> None:
        with self._lock:
            self._counts.clear()
            self._dirty = 1
            self.save()

    def flush(self) -> None:
        with self._lock:
            if self._dirty:
                self.save()


class GlobalTypingLearner:
    """Opt-in system-wide learner backed by pynput.

    It keeps only the current in-memory word buffer and persists normalized
    word counts to PersonalLexicon. It does not persist raw key events or
    sentences.
    """

    MODIFIER_NAMES = {
        "ctrl",
        "ctrl_l",
        "ctrl_r",
        "alt",
        "alt_l",
        "alt_r",
        "alt_gr",
        "cmd",
        "cmd_l",
        "cmd_r",
    }

    def __init__(self, lexicon: PersonalLexicon) -> None:
        self.lexicon = lexicon
        self._listener = None
        self._buffer: list[str] = []
        self._modifiers: set[str] = set()
        self._events: queue.SimpleQueue[tuple[str, str]] = queue.SimpleQueue()
        self._lock = threading.RLock()
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    def _key_name(self, key) -> str:
        return getattr(key, "name", "") or ""

    def _commit_buffer(self) -> None:
        if not self._buffer:
            return
        word = "".join(self._buffer)
        self._buffer.clear()
        if self.lexicon.record_word(word):
            normalized = _normalize_word(word)
            if normalized:
                self._events.put(("word", normalized))

    def _on_press(self, key) -> None:
        from pynput import keyboard

        with self._lock:
            name = self._key_name(key)
            if name in self.MODIFIER_NAMES:
                self._modifiers.add(name)
                return

            if key == keyboard.Key.backspace:
                if self._buffer:
                    self._buffer.pop()
                return

            if key in (keyboard.Key.space, keyboard.Key.enter, keyboard.Key.tab):
                self._commit_buffer()
                return

            if self._modifiers:
                return

            if isinstance(key, keyboard.KeyCode):
                ch = key.char
                if not ch:
                    return
                if ch.isalpha() or ch in "'’-":
                    self._buffer.append(ch)
                else:
                    self._commit_buffer()

    def _on_release(self, key) -> None:
        with self._lock:
            name = self._key_name(key)
            if name in self.MODIFIER_NAMES:
                self._modifiers.discard(name)

    def start(self) -> tuple[bool, str]:
        if self._running:
            return True, "already running"
        try:
            from pynput import keyboard

            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
            )
            self._listener.start()
        except Exception as exc:
            self._listener = None
            self._running = False
            return False, str(exc)

        self._running = True
        self._events.put(("status", "global learning on"))
        return True, "global learning on"

    def stop(self) -> None:
        if not self._running:
            return
        with self._lock:
            self._commit_buffer()
            listener = self._listener
            self._listener = None
            self._running = False

        if listener is not None:
            try:
                listener.stop()
            except Exception:
                pass

        self.lexicon.flush()
        self._events.put(("status", "global learning off"))

    def learn_text(self, text: str) -> int:
        count = self.lexicon.import_text(text)
        if count:
            self._events.put(("status", f"learned {count} clipboard words"))
        return count

    def drain_events(self, limit: int = 100) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for _ in range(max(1, limit)):
            try:
                out.append(self._events.get_nowait())
            except queue.Empty:
                break
        return out
