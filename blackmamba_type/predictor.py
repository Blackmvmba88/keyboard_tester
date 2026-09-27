from __future__ import annotations

from dataclasses import dataclass, field

from .learning import PersonalLexicon


DEFAULT_TERMS = [
    "programación",
    "programar",
    "programa",
    "proyecto",
    "proceso",
    "producción",
    "prototipo",
    "problema",
    "profesional",
    "prompt",
    "python",
    "pipeline",
    "predicción",
    "privacidad",
    "perfil",
    "prueba",
    "sistema",
    "interfaz",
    "teclado",
    "memoria",
    "música",
    "modelo",
    "motor",
    "modo",
    "contexto",
    "control",
    "código",
]


@dataclass
class PrefixPredictor:
    terms: list[str] = field(default_factory=lambda: list(DEFAULT_TERMS))
    lexicon: PersonalLexicon | None = None
    _usage: dict[str, int] = field(default_factory=dict)

    def suggest(self, prefix: str, limit: int = 6) -> list[str]:
        p = (prefix or "").strip().casefold()
        if not p:
            return []

        candidates: dict[str, tuple[int, int, int, str]] = {}

        for term in self.terms:
            if not term.casefold().startswith(p):
                continue
            persistent = self.lexicon.frequency(term) if self.lexicon else 0
            candidates[term] = (
                self._usage.get(term, 0),
                persistent,
                -len(term),
                term.casefold(),
            )

        if self.lexicon is not None:
            for term, persistent in self.lexicon.suggest(p, limit=max(limit * 4, 12)):
                current = candidates.get(term)
                score = (
                    self._usage.get(term, 0),
                    persistent,
                    -len(term),
                    term.casefold(),
                )
                if current is None or score > current:
                    candidates[term] = score

        ordered = sorted(
            candidates,
            key=lambda term: (
                -candidates[term][0],
                -candidates[term][1],
                len(term),
                term.casefold(),
            ),
        )
        return ordered[: max(1, limit)]

    def record_accept(self, term: str) -> None:
        self._usage[term] = self._usage.get(term, 0) + 1
        if self.lexicon is not None:
            self.lexicon.record_word(term)
