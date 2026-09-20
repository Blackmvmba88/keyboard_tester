from __future__ import annotations

import sys
from collections import deque

from PySide6.QtCore import QPoint, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QKeySequence, QPainter, QPen, QShortcut, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .metrics import SessionMetrics
from .predictor import PrefixPredictor
from .preferences import THEMES, UserPreferences


def build_qss(theme_name: str) -> str:
    p = THEMES.get(theme_name, THEMES["Mamba"])
    return f"""
QWidget {{
    background: {p["bg"]};
    color: {p["text"]};
    font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}}
QMainWindow {{ background: {p["bg"]}; }}
QFrame#TopBar {{
    background: {p["panel"]};
    border: 1px solid {p["border"]};
    border-radius: 14px;
}}
QLabel#Brand {{
    color: {p["bright"]};
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#Mode {{
    color: {p["accent"]};
    font-size: 11px;
    font-weight: 700;
}}
QLabel#Subtle {{
    color: {p["muted"]};
    font-size: 11px;
}}
QFrame#EditorCard, QFrame#MetricCard, QFrame#CandidateCard, QFrame#EmoticonCard {{
    background: {p["panel"]};
    border: 1px solid {p["border"]};
    border-radius: 16px;
}}
QPlainTextEdit#Editor {{
    background: transparent;
    color: {p["bright"]};
    border: none;
    selection-background-color: {p["selection"]};
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 24px;
    padding: 18px;
}}
QListWidget#Candidates, QListWidget#Emoticons {{
    background: transparent;
    border: none;
    outline: none;
    font-size: 15px;
}}
QListWidget#Candidates::item, QListWidget#Emoticons::item {{
    padding: 9px 11px;
    margin: 2px 0px;
    border-radius: 9px;
}}
QListWidget#Candidates::item:selected, QListWidget#Emoticons::item:selected {{
    background: {p["accent_soft"]};
    color: {p["accent"]};
}}
QPushButton, QComboBox, QLineEdit {{
    background: {p["panel_alt"]};
    color: {p["text"]};
    border: 1px solid {p["border"]};
    border-radius: 9px;
    padding: 8px 10px;
}}
QPushButton:hover, QComboBox:hover, QLineEdit:hover {{
    border-color: {p["accent"]};
}}
QLineEdit:focus, QComboBox:focus {{
    border-color: {p["accent"]};
}}
"""


class Sparkline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.values: deque[float] = deque(maxlen=60)
        self.setMinimumHeight(52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def push(self, value: float) -> None:
        self.values.append(max(0.0, float(value)))
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(4, 4, -4, -4)
        theme = THEMES.get(
            getattr(self.window(), "preferences", UserPreferences()).theme,
            THEMES["Mamba"],
        )
        painter.setPen(QPen(QColor(theme["border"]), 1))
        painter.drawRoundedRect(QRectF(rect), 8, 8)
        if len(self.values) < 2:
            return

        vals = list(self.values)
        vmax = max(max(vals), 1.0)
        step = rect.width() / max(len(vals) - 1, 1)
        points = []
        for i, value in enumerate(vals):
            x = rect.left() + i * step
            y = rect.bottom() - (value / vmax) * max(rect.height() - 6, 1)
            points.append(QPoint(int(x), int(y)))

        painter.setPen(QPen(QColor(theme["accent"]), 2))
        for a, b in zip(points, points[1:]):
            painter.drawLine(a, b)


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "0", parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        self.title = QLabel(title)
        self.title.setObjectName("Subtle")
        self.value = QLabel(value)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.value.setFont(font)
        layout.addWidget(self.title)
        layout.addWidget(self.value)


class WriterEdit(QPlainTextEdit):
    request_move = Signal(int)
    request_accept = Signal()
    request_dismiss = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        mods = event.modifiers()
        candidates_active = bool(self.property("candidatesActive"))

        if mods == Qt.KeyboardModifier.NoModifier and candidates_active:
            if key == Qt.Key.Key_Down:
                self.request_move.emit(1)
                event.accept()
                return
            if key == Qt.Key.Key_Up:
                self.request_move.emit(-1)
                event.accept()
                return
            if key in (Qt.Key.Key_Tab, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.request_accept.emit()
                event.accept()
                return
            if key == Qt.Key.Key_Escape:
                self.request_dismiss.emit()
                event.accept()
                return

        super().keyPressEvent(event)


class BlackMambaTypeWindow(QMainWindow):
    def __init__(self, preferences: UserPreferences | None = None) -> None:
        super().__init__()
        self.setWindowTitle("BLACKMAMBA TYPE — Iteration 02")
        self.resize(1240, 800)

        self.preferences = preferences or UserPreferences.load()
        self.predictor = PrefixPredictor()
        self.metrics = SessionMetrics()
        self._candidate_visible = True
        self._focus_mode = False

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(12)

        top = QFrame()
        top.setObjectName("TopBar")
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(16, 12, 16, 12)
        brand = QLabel("BLACKMAMBA TYPE")
        brand.setObjectName("Brand")
        mode = QLabel("TYPE WORLD · LOCAL · ITER 02")
        mode.setObjectName("Mode")
        hint = QLabel("↑ ↓ choose · Tab / Enter accept · Esc dismiss")
        hint.setObjectName("Subtle")
        top_layout.addWidget(brand)
        top_layout.addSpacing(12)
        top_layout.addWidget(mode)
        top_layout.addStretch(1)
        top_layout.addWidget(hint)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.setCurrentText(self.preferences.theme)
        self.theme_combo.currentTextChanged.connect(self._change_theme)
        top_layout.addWidget(self.theme_combo)

        self.focus_button = QPushButton("Focus")
        self.focus_button.clicked.connect(self.toggle_focus_mode)
        top_layout.addWidget(self.focus_button)
        outer.addWidget(top)

        body = QHBoxLayout()
        body.setSpacing(12)
        outer.addLayout(body, 1)

        editor_card = QFrame()
        editor_card.setObjectName("EditorCard")
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(10, 10, 10, 10)

        header = QHBoxLayout()
        title = QLabel("WRITER")
        title.setObjectName("Mode")
        self.prefix_label = QLabel("waiting for input")
        self.prefix_label.setObjectName("Subtle")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.prefix_label)
        editor_layout.addLayout(header)

        self.editor = WriterEdit()
        self.editor.setObjectName("Editor")
        self.editor.setPlaceholderText(
            "Escribe aquí…\n\nPrueba:  pro\nLuego usa ↑ ↓ y Tab."
        )
        editor_layout.addWidget(self.editor, 1)

        quick = QHBoxLayout()
        self.copy_button = QPushButton("Copy all")
        self.copy_button.clicked.connect(self._copy_all)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_editor)
        quick.addWidget(self.copy_button)
        quick.addWidget(self.clear_button)
        quick.addStretch(1)
        editor_layout.addLayout(quick)

        body.addWidget(editor_card, 3)

        self.side_widget = QWidget()
        side = QVBoxLayout(self.side_widget)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        body.addWidget(self.side_widget, 1)

        candidate_card = QFrame()
        candidate_card.setObjectName("CandidateCard")
        candidate_layout = QVBoxLayout(candidate_card)
        candidate_layout.setContentsMargins(12, 12, 12, 12)
        candidate_title = QLabel("CANDIDATES")
        candidate_title.setObjectName("Mode")
        candidate_layout.addWidget(candidate_title)

        self.candidates = QListWidget()
        self.candidates.setObjectName("Candidates")
        candidate_layout.addWidget(self.candidates)
        side.addWidget(candidate_card, 2)

        emoticon_card = QFrame()
        emoticon_card.setObjectName("EmoticonCard")
        emoticon_layout = QVBoxLayout(emoticon_card)
        emoticon_layout.setContentsMargins(12, 12, 12, 12)

        emoticon_title = QLabel("MY EMOTICONS")
        emoticon_title.setObjectName("Mode")
        emoticon_layout.addWidget(emoticon_title)

        self.emoticons = QListWidget()
        self.emoticons.setObjectName("Emoticons")
        self.emoticons.setMaximumHeight(150)
        self.emoticons.itemDoubleClicked.connect(lambda _: self._insert_selected_emoticon())
        emoticon_layout.addWidget(self.emoticons)

        self.emoticon_input = QLineEdit()
        self.emoticon_input.setPlaceholderText("Añade emoji o emoticon…")
        self.emoticon_input.returnPressed.connect(self._add_emoticon)
        emoticon_layout.addWidget(self.emoticon_input)

        emoticon_actions = QHBoxLayout()
        insert_emoticon = QPushButton("Insert")
        insert_emoticon.clicked.connect(self._insert_selected_emoticon)
        add_emoticon = QPushButton("+")
        add_emoticon.clicked.connect(self._add_emoticon)
        remove_emoticon = QPushButton("−")
        remove_emoticon.clicked.connect(self._remove_selected_emoticon)
        emoticon_actions.addWidget(insert_emoticon)
        emoticon_actions.addWidget(add_emoticon)
        emoticon_actions.addWidget(remove_emoticon)
        emoticon_layout.addLayout(emoticon_actions)
        side.addWidget(emoticon_card, 2)

        metric_row_a = QHBoxLayout()
        self.wpm_card = MetricCard("WPM")
        self.words_card = MetricCard("WORDS")
        metric_row_a.addWidget(self.wpm_card)
        metric_row_a.addWidget(self.words_card)
        side.addLayout(metric_row_a)

        metric_row_b = QHBoxLayout()
        self.cps_card = MetricCard("CHARS / S")
        self.saved_card = MetricCard("SAVED KEYS")
        metric_row_b.addWidget(self.cps_card)
        metric_row_b.addWidget(self.saved_card)
        side.addLayout(metric_row_b)

        spark_card = QFrame()
        spark_card.setObjectName("MetricCard")
        spark_layout = QVBoxLayout(spark_card)
        spark_layout.setContentsMargins(14, 12, 14, 12)
        spark_title = QLabel("LIVE SPEED")
        spark_title.setObjectName("Subtle")
        self.spark = Sparkline()
        spark_layout.addWidget(spark_title)
        spark_layout.addWidget(self.spark)
        side.addWidget(spark_card)

        footer = QHBoxLayout()
        self.status = QLabel("ITERATION 02 · themes + personal emoticon dock")
        self.status.setObjectName("Subtle")
        reset = QPushButton("Reset session")
        reset.clicked.connect(self.reset_session)
        footer.addWidget(self.status)
        footer.addStretch(1)
        footer.addWidget(reset)
        outer.addLayout(footer)

        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.request_move.connect(self._move_candidate)
        self.editor.request_accept.connect(self._accept_candidate)
        self.editor.request_dismiss.connect(self._dismiss_candidates)

        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self._refresh_metrics)
        self.timer.start()

        self.focus_shortcut = QShortcut(QKeySequence("Ctrl+Shift+F"), self)
        self.focus_shortcut.activated.connect(self.toggle_focus_mode)
        self.emoticon_shortcut = QShortcut(QKeySequence("Ctrl+Shift+E"), self)
        self.emoticon_shortcut.activated.connect(self._insert_selected_emoticon)
        self.theme_shortcut = QShortcut(QKeySequence("Ctrl+Shift+T"), self)
        self.theme_shortcut.activated.connect(self._cycle_theme)

        self._reload_emoticons()
        self._refresh_candidates()
        self.editor.setFocus()

    def current_prefix(self) -> str:
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText().strip()

    def _on_text_changed(self) -> None:
        self.metrics.observe_text(self.editor.toPlainText())
        self._candidate_visible = True
        self._refresh_candidates()
        self._refresh_metrics()

    def _refresh_candidates(self) -> None:
        prefix = self.current_prefix()
        self.prefix_label.setText(f'prefix: "{prefix}"' if prefix else "waiting for input")
        suggestions = self.predictor.suggest(prefix, limit=6) if self._candidate_visible else []

        self.candidates.clear()
        for suggestion in suggestions:
            self.candidates.addItem(QListWidgetItem(suggestion))

        active = self.candidates.count() > 0
        self.editor.setProperty("candidatesActive", active)
        if active:
            self.candidates.setCurrentRow(0)

    def _move_candidate(self, delta: int) -> None:
        count = self.candidates.count()
        if not count:
            return
        row = self.candidates.currentRow()
        if row < 0:
            row = 0
        self.candidates.setCurrentRow((row + delta) % count)

    def _accept_candidate(self) -> None:
        item = self.candidates.currentItem()
        if item is None:
            return

        suggestion = item.text()
        prefix = self.current_prefix()
        if not prefix or not suggestion.lower().startswith(prefix.lower()):
            return

        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        typed_len = len(cursor.selectedText())
        cursor.insertText(suggestion)
        self.editor.setTextCursor(cursor)

        saved = max(0, len(suggestion) - typed_len)
        self.metrics.record_completion(prefix, suggestion, saved)
        self.predictor.record_accept(suggestion)
        self.status.setText(
            f'accepted "{suggestion}" · saved {saved} keystroke{"s" if saved != 1 else ""}'
        )

        self._candidate_visible = False
        self._refresh_candidates()

    def _dismiss_candidates(self) -> None:
        self._candidate_visible = False
        self.candidates.clear()
        self.editor.setProperty("candidatesActive", False)
        self.status.setText("candidates dismissed · keep typing to reopen")

    def _refresh_metrics(self) -> None:
        snap = self.metrics.snapshot()
        self.wpm_card.value.setText(f"{snap.wpm:.0f}")
        self.words_card.value.setText(str(snap.words))
        self.cps_card.value.setText(f"{snap.chars_per_second:.1f}")
        self.saved_card.value.setText(str(snap.saved_keystrokes))
        self.spark.push(snap.wpm)

    def _reload_emoticons(self) -> None:
        self.emoticons.clear()
        for emoticon in self.preferences.emoticons:
            self.emoticons.addItem(QListWidgetItem(emoticon))
        if self.emoticons.count():
            self.emoticons.setCurrentRow(0)

    def _insert_selected_emoticon(self) -> None:
        item = self.emoticons.currentItem()
        if item is None:
            return
        cursor = self.editor.textCursor()
        cursor.insertText(item.text())
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        self.status.setText(f'inserted emoticon "{item.text()}"')

    def _add_emoticon(self) -> None:
        value = self.emoticon_input.text().strip()
        if not value:
            return
        if value not in self.preferences.emoticons:
            self.preferences.emoticons.append(value)
            self.preferences.save()
            self._reload_emoticons()
            self.emoticons.setCurrentRow(self.preferences.emoticons.index(value))
            self.status.setText(f'added emoticon "{value}"')
        self.emoticon_input.clear()
        self.editor.setFocus()

    def _remove_selected_emoticon(self) -> None:
        item = self.emoticons.currentItem()
        if item is None:
            return
        value = item.text()
        if value in self.preferences.emoticons:
            self.preferences.emoticons.remove(value)
            self.preferences.save()
            self._reload_emoticons()
            self.status.setText(f'removed emoticon "{value}"')

    def _change_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return
        self.preferences.theme = theme_name
        self.preferences.save()
        QApplication.instance().setStyleSheet(build_qss(theme_name))
        self.spark.update()
        self.status.setText(f"theme: {theme_name}")

    def _cycle_theme(self) -> None:
        names = list(THEMES)
        current = names.index(self.preferences.theme) if self.preferences.theme in names else 0
        self.theme_combo.setCurrentText(names[(current + 1) % len(names)])

    def toggle_focus_mode(self) -> None:
        self._focus_mode = not self._focus_mode
        self.side_widget.setVisible(not self._focus_mode)
        self.focus_button.setText("Exit focus" if self._focus_mode else "Focus")
        self.status.setText("focus mode on" if self._focus_mode else "focus mode off")
        self.editor.setFocus()

    def _copy_all(self) -> None:
        QApplication.clipboard().setText(self.editor.toPlainText())
        self.status.setText("copied full writer text")

    def _clear_editor(self) -> None:
        self.editor.clear()
        self.status.setText("writer cleared")
        self.editor.setFocus()

    def reset_session(self) -> None:
        self.metrics.reset(self.editor.toPlainText())
        self.spark.values.clear()
        self.status.setText("session metrics reset")
        self._refresh_metrics()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("BLACKMAMBA TYPE")

    preferences = UserPreferences.load()
    app.setStyleSheet(build_qss(preferences.theme))

    window = BlackMambaTypeWindow(preferences)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
