from __future__ import annotations

import sys
from collections import deque

from PySide6.QtCore import QPoint, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QPainter, QPen, QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
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


APP_QSS = """
QWidget {
    background: #090b10;
    color: #e8edf5;
    font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}
QMainWindow { background: #090b10; }
QFrame#TopBar {
    background: #0e1219;
    border: 1px solid #1c2430;
    border-radius: 14px;
}
QLabel#Brand {
    color: #f2f6fb;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1px;
}
QLabel#Mode {
    color: #73f6b1;
    font-size: 11px;
    font-weight: 700;
}
QLabel#Subtle {
    color: #748092;
    font-size: 11px;
}
QFrame#EditorCard, QFrame#MetricCard, QFrame#CandidateCard {
    background: #0e1219;
    border: 1px solid #1c2430;
    border-radius: 16px;
}
QPlainTextEdit#Editor {
    background: transparent;
    color: #f8fafc;
    border: none;
    selection-background-color: #263343;
    font-family: "SF Mono", "Menlo", monospace;
    font-size: 24px;
    padding: 18px;
}
QListWidget#Candidates {
    background: transparent;
    border: none;
    outline: none;
    font-size: 15px;
}
QListWidget#Candidates::item {
    padding: 10px 12px;
    margin: 2px 0px;
    border-radius: 9px;
}
QListWidget#Candidates::item:selected {
    background: #17251f;
    color: #8cffbd;
}
QPushButton {
    background: #141a23;
    border: 1px solid #273140;
    border-radius: 9px;
    padding: 8px 12px;
}
QPushButton:hover { border-color: #4b5d74; }
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
        painter.setPen(QPen(QColor("#1c2430"), 1))
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

        painter.setPen(QPen(QColor("#6ef0a6"), 2))
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
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BLACKMAMBA TYPE — Iteration 01")
        self.resize(1180, 760)

        self.predictor = PrefixPredictor()
        self.metrics = SessionMetrics()
        self._candidate_visible = True

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
        mode = QLabel("TYPE WORLD · LOCAL")
        mode.setObjectName("Mode")
        hint = QLabel("↑ ↓ choose · Tab / Enter accept · Esc dismiss")
        hint.setObjectName("Subtle")
        top_layout.addWidget(brand)
        top_layout.addSpacing(12)
        top_layout.addWidget(mode)
        top_layout.addStretch(1)
        top_layout.addWidget(hint)
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
        body.addWidget(editor_card, 3)

        side = QVBoxLayout()
        side.setSpacing(12)
        body.addLayout(side, 1)

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
        self.status = QLabel("ITERATION 01 · no history is persisted yet")
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

    def reset_session(self) -> None:
        self.metrics.reset(self.editor.toPlainText())
        self.status.setText("session metrics reset")
        self._refresh_metrics()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("BLACKMAMBA TYPE")
    app.setStyleSheet(APP_QSS)

    window = BlackMambaTypeWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
