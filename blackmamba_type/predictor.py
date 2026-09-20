from __future__ import annotations

from dataclasses import dataclass, field


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
    _usage: dict[str, int] = field(default_factory=dict)

    def suggest(self, prefix: str, limit: int = 6) -> list[str]:
        p = (prefix or "").strip().casefold()
        if not p:
            return []

        matches = [term for term in self.terms if term.casefold().startswith(p)]
        matches.sort(
            key=lambda term: (
                -self._usage.get(term, 0),
                len(term),
                term.casefold(),
            )
        )
        return matches[: max(1, limit)]

    def record_accept(self, term: str) -> None:
        self._usage[term] = self._usage.get(term, 0) + 1
