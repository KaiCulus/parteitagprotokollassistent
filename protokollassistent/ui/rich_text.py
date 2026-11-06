"""Rich-Text-Editor für Textblöcke und Umwandlung Editor ↔ Datenmodell."""
from __future__ import annotations

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt

from ..core.model import Run, merge_runs
from ..core.placeholders import PLACEHOLDER_RE
from . import theme

P = QtGui.QTextFormat.Property
BOLD, NORMAL = 700, 400
LINE_SEPARATOR = " "        # entsteht im Editor durch Umschalt+Enter
OBJECT_CHAR = "￼"
OWN_MIME = "application/x-protokollassistent"


# ── Formate ↔ Run ────────────────────────────────────────────────────────────
def run_from_format(text: str, f: QtGui.QTextCharFormat) -> Run:
    r = Run(text)
    if f.hasProperty(P.ForegroundBrush):
        b = f.foreground()
        if b.style() != Qt.BrushStyle.NoBrush:
            r.color = b.color().name()
    if f.hasProperty(P.BackgroundBrush):
        b = f.background()
        if b.style() != Qt.BrushStyle.NoBrush:
            r.bg = b.color().name()
    if f.hasProperty(P.FontPointSize) and f.fontPointSize() > 0:
        r.size = round(f.fontPointSize(), 1)
    r.bold = f.fontWeight() >= 600
    r.italic = f.fontItalic()
    r.underline = f.fontUnderline()
    r.strike = f.fontStrikeOut()
    return r


def format_from_run(r: Run) -> QtGui.QTextCharFormat:
    f = QtGui.QTextCharFormat()
    if r.color:
        f.setForeground(QtGui.QColor(r.color))
    if r.bg:
        f.setBackground(QtGui.QColor(r.bg))
    if r.size:
        f.setFontPointSize(r.size)
    if r.bold:
        f.setFontWeight(BOLD)
    if r.italic:
        f.setFontItalic(True)
    if r.underline:
        f.setFontUnderline(True)
    if r.strike:
        f.setFontStrikeOut(True)
    return f


# ── Dokument ↔ Zeilen ────────────────────────────────────────────────────────
def lines_from_document(doc: QtGui.QTextDocument) -> list[list[Run]]:
    lines: list[list[Run]] = []
    blk = doc.begin()
    while blk.isValid():
        line: list[Run] = []
        it = blk.begin()
        while not it.atEnd():
            frag = it.fragment()
            if frag.isValid():
                parts = frag.text().replace(OBJECT_CHAR, "").split(LINE_SEPARATOR)
                for j, part in enumerate(parts):
                    if j > 0:
                        lines.append(merge_runs(line))
                        line = []
                    if part:
                        line.append(run_from_format(part, frag.charFormat()))
            it += 1
        lines.append(merge_runs(line))
        blk = blk.next()
    return lines or [[]]


def lines_to_document(doc: QtGui.QTextDocument, lines: list[list[Run]]) -> None:
    doc.clear()
    cur = QtGui.QTextCursor(doc)
    for i, line in enumerate(lines):
        if i:
            cur.insertBlock(QtGui.QTextBlockFormat(), QtGui.QTextCharFormat())
        for r in line:
            cur.insertText(r.text, format_from_run(r))


# ── Widgets ──────────────────────────────────────────────────────────────────
class PlaceholderHighlighter(QtGui.QSyntaxHighlighter):
    """Färbt {{Systime}} & Co. im Editor blau – nur zur Anzeige, nicht gespeichert."""

    def __init__(self, doc):
        super().__init__(doc)
        self.fmt = QtGui.QTextCharFormat()
        self.fmt.setForeground(QtGui.QColor(theme.PLACEHOLDER_BLUE))
        self.fmt.setBackground(QtGui.QColor("#eef0ff"))

    def highlightBlock(self, text):
        for m in PLACEHOLDER_RE.finditer(text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt)


class BlockEditor(QtWidgets.QTextEdit):
    """Rich-Text-Editor: Einfügen von außen nur als reiner Text,
    Kopieren innerhalb des Editors behält die Formatierung."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(True)
        self.setTabChangesFocus(False)
        self._highlighter = PlaceholderHighlighter(self.document())

    def createMimeDataFromSelection(self):
        md = super().createMimeDataFromSelection()
        md.setData(OWN_MIME, b"1")
        return md

    def insertFromMimeData(self, source):
        if source.hasFormat(OWN_MIME):
            super().insertFromMimeData(source)
        elif source.hasText():
            self.insertPlainText(source.text())

    def set_lines(self, lines) -> None:
        lines_to_document(self.document(), lines)
        self.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def lines(self) -> list[list[Run]]:
        return lines_from_document(self.document())
