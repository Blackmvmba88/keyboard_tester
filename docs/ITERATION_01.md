# Iteration 01 — TYPE SHELL

Status: **implemented on `feat/type-iter-01-shell`**

This iteration creates the first executable BLACKMAMBA TYPE desktop surface.

## Included

- native PySide6 desktop window
- BlackMamba visual shell
- writing editor
- live prefix detection
- local prefix candidate list
- `↑ / ↓` candidate navigation
- `Tab` or `Enter` to accept
- `Esc` to dismiss
- live WPM
- words
- characters per second
- saved-keystroke counter
- live speed sparkline
- session reset
- no network/server dependency

## Demo

Type:

```text
pro
```

The initial local dictionary can show candidates such as:

```text
programa
proceso
proyecto
programar
programación
producción
```

The ranking in Iteration 01 is deliberately simple. Persistent personal ranking arrives in later iterations.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 run_blackmamba_type.py
```

## Non-goals for Iteration 01

This cut does **not** yet:

- capture typing globally across macOS
- persist history
- store SQLite sessions
- perform AI/LLM completion
- read other applications' text context
- replace the existing diagnostics
- implement InputMethodKit
- implement global overlays

Those are intentionally deferred so the first cut remains visible, runnable, and testable.
