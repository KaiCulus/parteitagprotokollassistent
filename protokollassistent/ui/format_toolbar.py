"""Formatierungsleiste über dem Editor: Fett, Kursiv, Farben, Größe, Systemzeit …"""
from __future__ import annotations

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt

from ..core.placeholders import PLACEHOLDERS, SYSTIME
from . import theme
from .rich_text import BOLD, NORMAL, P, BlockEditor, run_from_format

SIZE_TARGET = "Ziel"


def swatch(color: str | None, size=14) -> QtGui.QIcon:
    pm = QtGui.QPixmap(size, size)
    if color:
        pm.fill(QtGui.QColor(color))
    else:
        pm.fill(Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pm)
        p.setPen(QtGui.QPen(QtGui.QColor("#888888")))
        p.drawRect(0, 0, size - 1, size - 1)
        p.drawLine(0, size - 1, size - 1, 0)
        p.end()
    return QtGui.QIcon(pm)


class FormatToolbar(QtWidgets.QWidget):
    def __init__(self, editor: BlockEditor, parent=None):
        super().__init__(parent)
        self.editor = editor
        bar = QtWidgets.QHBoxLayout(self)
        bar.setContentsMargins(0, 0, 0, 0)

        # Systemzeit – die wichtigste Funktion zuerst und gut sichtbar
        btn_time = QtWidgets.QPushButton("🕒 Systemzeit einfügen")
        btn_time.setToolTip(f"Fügt {SYSTIME} ein – wird beim Auslösen des Hotkeys durch die "
                            "aktuelle Uhrzeit ersetzt")
        btn_time.setStyleSheet(theme.PRIMARY_BUTTON.replace("14px 28px", "6px 12px")
                               .replace("11pt", "10pt"))
        btn_time.clicked.connect(lambda: self._insert(SYSTIME))
        bar.addWidget(btn_time)

        more = QtWidgets.QToolButton()
        more.setText("Weitere Platzhalter")
        more.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QtWidgets.QMenu(more)
        for token, desc in PLACEHOLDERS:
            menu.addAction(f"{token}  –  {desc}",
                           lambda checked=False, t=token: self._insert(t))
        more.setMenu(menu)
        bar.addWidget(more)
        bar.addSpacing(12)

        self.act_bold = self._fmt_action("F", "Fett (Strg+B)", "Ctrl+B", self._toggle_bold,
                                         lambda f: f.setBold(True), bar)
        self.act_italic = self._fmt_action("K", "Kursiv (Strg+I)", "Ctrl+I",
                                           self._toggle_italic, lambda f: f.setItalic(True), bar)
        self.act_under = self._fmt_action("U", "Unterstrichen (Strg+U)", "Ctrl+U",
                                          self._toggle_under, lambda f: f.setUnderline(True), bar)
        self.act_strike = self._fmt_action("S", "Durchgestrichen", None, self._toggle_strike,
                                           lambda f: f.setStrikeOut(True), bar)
        bar.addSpacing(8)

        self.btn_color = self._color_button("Schriftfarbe", theme.TEXT_COLORS, self._set_color,
                                            lambda: self.clear_props(P.ForegroundBrush))
        self.btn_bg = self._color_button("Hervorheben", theme.HIGHLIGHT_COLORS, self._set_bg,
                                         lambda: self.clear_props(P.BackgroundBrush))
        bar.addWidget(self.btn_color)
        bar.addWidget(self.btn_bg)
        bar.addSpacing(8)

        bar.addWidget(QtWidgets.QLabel("Größe:"))
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.setEditable(True)
        self.size_combo.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.NoInsert)
        self.size_combo.addItems([SIZE_TARGET] + theme.FONT_SIZES)
        self.size_combo.setToolTip("Schriftgröße in pt. „Ziel“ = Größe des Zieldokuments übernehmen")
        self.size_combo.setMinimumWidth(70)
        self.size_combo.textActivated.connect(self._set_size)
        bar.addWidget(self.size_combo)

        clr = QtWidgets.QToolButton()
        clr.setText("Formatierung entfernen")
        clr.setToolTip("Markierten Text auf die Formatierung des Zieldokuments zurücksetzen")
        clr.clicked.connect(self._clear_all)
        bar.addWidget(clr)
        bar.addStretch()

        editor.currentCharFormatChanged.connect(self.sync)

    # ── Aufbau-Helfer ──
    def _fmt_action(self, text, tip, shortcut, slot, font_mod, bar):
        act = QtGui.QAction(text, self, checkable=True)
        act.setToolTip(tip)
        if shortcut:
            act.setShortcut(QtGui.QKeySequence(shortcut))
            act.setShortcutContext(Qt.ShortcutContext.WidgetShortcut)
            self.editor.addAction(act)
        act.triggered.connect(slot)
        btn = QtWidgets.QToolButton()
        btn.setDefaultAction(act)
        f = btn.font()
        font_mod(f)
        f.setPointSize(f.pointSize() + 1)
        btn.setFont(f)
        btn.setMinimumWidth(30)
        bar.addWidget(btn)
        return act

    def _color_button(self, text, presets, on_pick, on_clear):
        btn = QtWidgets.QToolButton()
        btn.setText(text)
        btn.setIcon(swatch(None))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QtWidgets.QMenu(btn)
        for name, col in presets:
            menu.addAction(swatch(col), name, lambda checked=False, c=col: on_pick(c))
        menu.addSeparator()

        def custom():
            c = QtWidgets.QColorDialog.getColor(parent=self, title=text)
            if c.isValid():
                on_pick(c.name())
        menu.addAction("Andere Farbe …", custom)
        menu.addAction(swatch(None), "Keine (Format des Zieldokuments)", on_clear)
        btn.setMenu(menu)
        return btn

    # ── Aktionen ──
    def _insert(self, token):
        self.editor.insertPlainText(token)
        self.editor.setFocus()

    def _merge(self, fmt):
        self.editor.mergeCurrentCharFormat(fmt)
        self.editor.setFocus()

    def _toggle_bold(self, on):
        f = QtGui.QTextCharFormat()
        f.setFontWeight(BOLD if on else NORMAL)
        self._merge(f)

    def _toggle_italic(self, on):
        f = QtGui.QTextCharFormat()
        f.setFontItalic(on)
        self._merge(f)

    def _toggle_under(self, on):
        f = QtGui.QTextCharFormat()
        f.setFontUnderline(on)
        self._merge(f)

    def _toggle_strike(self, on):
        f = QtGui.QTextCharFormat()
        f.setFontStrikeOut(on)
        self._merge(f)

    def _set_color(self, col):
        f = QtGui.QTextCharFormat()
        f.setForeground(QtGui.QColor(col))
        self._merge(f)

    def _set_bg(self, col):
        f = QtGui.QTextCharFormat()
        f.setBackground(QtGui.QColor(col))
        self._merge(f)

    def _set_size(self, text):
        text = text.strip().replace(",", ".")
        if not text or text.lower() == SIZE_TARGET.lower():
            self.clear_props(P.FontPointSize)
            return
        try:
            size = float(text)
        except ValueError:
            return
        if 4 <= size <= 200:
            f = QtGui.QTextCharFormat()
            f.setFontPointSize(size)
            self._merge(f)

    def clear_props(self, *props):
        """Entfernt einzelne Eigenschaften (z. B. Farbe) – im markierten Text Zeichen für
        Zeichen, damit andere Formatierungen erhalten bleiben."""
        c = self.editor.textCursor()
        if c.hasSelection():
            start, end = c.selectionStart(), c.selectionEnd()
            cur = QtGui.QTextCursor(self.editor.document())
            cur.beginEditBlock()
            for i in range(start, end):
                cur.setPosition(i)
                cur.setPosition(i + 1, QtGui.QTextCursor.MoveMode.KeepAnchor)
                f = cur.charFormat()
                for p in props:
                    f.clearProperty(p)
                cur.setCharFormat(f)
            cur.endEditBlock()
        else:
            f = self.editor.currentCharFormat()
            for p in props:
                f.clearProperty(p)
            self.editor.setCurrentCharFormat(f)
        self.sync(self.editor.currentCharFormat())
        self.editor.setFocus()

    def _clear_all(self):
        c = self.editor.textCursor()
        if c.hasSelection():
            c.setCharFormat(QtGui.QTextCharFormat())
        self.editor.setCurrentCharFormat(QtGui.QTextCharFormat())
        self.sync(self.editor.currentCharFormat())
        self.editor.setFocus()

    def sync(self, f):
        """Schaltflächen an die Formatierung an der Cursorposition anpassen."""
        for act, val in ((self.act_bold, f.fontWeight() >= 600),
                         (self.act_italic, f.fontItalic()),
                         (self.act_under, f.fontUnderline()),
                         (self.act_strike, f.fontStrikeOut())):
            act.blockSignals(True)
            act.setChecked(val)
            act.blockSignals(False)
        r = run_from_format("", f)
        self.btn_color.setIcon(swatch(r.color))
        self.btn_bg.setIcon(swatch(r.bg))
        self.size_combo.blockSignals(True)
        self.size_combo.setCurrentText(f"{r.size:g}" if r.size else SIZE_TARGET)
        self.size_combo.blockSignals(False)
