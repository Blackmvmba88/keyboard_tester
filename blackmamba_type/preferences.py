from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_EMOTICONS = [
    "😂", "🔥", "😎", "🤯", "🧠", "⚡", "🚀", "✨",
    "👑", "🎵", "🎧", "🐍", "💀", "❤️",
    "xD", ":D", ";)", ":P", "¯\\_(ツ)_/¯", "(ง'̀-'́)ง",
]

THEMES: dict[str, dict[str, str]] = {
    "Mamba": {
        "bg": "#090b10",
        "panel": "#0e1219",
        "panel_alt": "#141a23",
        "border": "#1c2430",
        "text": "#e8edf5",
        "bright": "#f8fafc",
        "muted": "#748092",
        "accent": "#73f6b1",
        "accent_soft": "#17251f",
        "selection": "#263343",
    },
    "Neon": {
        "bg": "#080611",
        "panel": "#120d1f",
        "panel_alt": "#1a1229",
        "border": "#35234a",
        "text": "#f3ecff",
        "bright": "#ffffff",
        "muted": "#9d8fb4",
        "accent": "#c084fc",
        "accent_soft": "#26183a",
        "selection": "#3b2654",
    },
    "Ocean": {
        "bg": "#071017",
        "panel": "#0c1822",
        "panel_alt": "#10212d",
        "border": "#1c3444",
        "text": "#e8f7ff",
        "bright": "#ffffff",
        "muted": "#7f9ead",
        "accent": "#67e8f9",
        "accent_soft": "#102b31",
        "selection": "#173846",
    },
    "Paper": {
        "bg": "#f2efe7",
        "panel": "#fffdf8",
        "panel_alt": "#f7f1e5",
        "border": "#d6cfbf",
        "text": "#28251f",
        "bright": "#11100e",
        "muted": "#777166",
        "accent": "#0f766e",
        "accent_soft": "#dff3ef",
        "selection": "#cfe6e2",
    },
}


@dataclass
class UserPreferences:
    theme: str = "Mamba"
    emoticons: list[str] = field(default_factory=lambda: list(DEFAULT_EMOTICONS))

    @staticmethod
    def path() -> Path:
        return Path.home() / ".blackmamba_type" / "settings.json"

    @classmethod
    def load(cls) -> "UserPreferences":
        path = cls.path()
        if not path.exists():
            return cls()

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return cls()

        theme = raw.get("theme", "Mamba")
        if theme not in THEMES:
            theme = "Mamba"

        emoticons = raw.get("emoticons", list(DEFAULT_EMOTICONS))
        if not isinstance(emoticons, list):
            emoticons = list(DEFAULT_EMOTICONS)
        emoticons = [str(item) for item in emoticons if str(item).strip()]

        return cls(theme=theme, emoticons=emoticons or list(DEFAULT_EMOTICONS))

    def save(self) -> None:
        path = self.path()
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "theme": self.theme,
            "emoticons": self.emoticons,
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
