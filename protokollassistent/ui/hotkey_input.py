"""Eingabefeld für einen Hotkey (Modifikatoren + Taste) mit Live-Konfliktanzeige."""
from __future__ import annotations

import html
from typing import Callable

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal

from ..core.combos import combo_label, combo_to_str, key_label, parse_combo
from ..core.conflicts import CheckResult
from ..core.constants import KEY_CHOICES, MOD_LABELS, MODIFIERS
from ..core.model import block_summary
from . import theme


def describe_result(res: CheckResult) -> str:
    """CheckResult → HTML für die Statuszeile."""
    if res.invalid:
        return f"<span style='color:{theme.ERROR_RED}'>✖ {html.escape(res.invalid)}</span>"
    if not res.has_conflict:
        return f"<span style='color:{theme.OK_GREEN}'>✔ Keine bekannte Belegung.</span>"
    items = [f"<li><b>Protokollassistent</b>: Textblock „{html.escape(block_summary(b))}“ "
             "– wird beim Speichern überschrieben</li>" for b in res.own]
    items += [f"<li><b>{html.escape(s)}</b>: {html.escape(d)}</li>" for s, d in res.system]
    return (f"<span style='color:{theme.WARN_ORANGE}'><b>⚠ Bereits belegt:</b></span>"
            f"<ul style='margin-top:2px'>{''.join(items)}</ul>")


class HotkeyInput(QtWidgets.QWidget):
    changed = Signal(str)

    def __init__(self, fam: str, check: Callable[[str], CheckResult],
                 suggest: Callable[[], str | None], parent=None):
        super().__init__(parent)
        self.fam = fam
        self._check = check
        self._suggest = suggest
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        row = QtWidgets.QHBoxLayout()
        self.checks: dict[str, QtWidgets.QCheckBox] = {}
        for m in MODIFIERS:
            cb = QtWidgets.QCheckBox(MOD_LABELS[fam][m])
            cb.toggled.connect(self._update)
            row.addWidget(cb)
            self.checks[m] = cb
        row.addWidget(QtWidgets.QLabel("+"))
        self.key = QtWidgets.QComboBox()
        for k in KEY_CHOICES:
            self.key.addItem(key_label(k), k)
        self.key.currentIndexChanged.connect(self._update)
        row.addWidget(self.key)
        row.addSpacing(10)
        self.preview = QtWidgets.QLabel()
        row.addWidget(self.preview)
        row.addStretch()
        btn = QtWidgets.QPushButton("Freie Kombination vorschlagen")
        btn.clicked.connect(self._do_suggest)
        row.addWidget(btn)
        lay.addLayout(row)

        self.status = QtWidgets.QLabel()
        self.status.setWordWrap(True)
        self.status.setTextFormat(Qt.TextFormat.RichText)
        self.status.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.status.setMinimumHeight(40)
        lay.addWidget(self.status)

    def set_combo(self, combo: str) -> None:
        p = parse_combo(combo)
        if not p:
            return
        mods, key = p
        for m, cb in self.checks.items():
            cb.blockSignals(True)
            cb.setChecked(m in mods)
            cb.blockSignals(False)
        i = self.key.findData(key)
        if i >= 0:
            self.key.blockSignals(True)
            self.key.setCurrentIndex(i)
            self.key.blockSignals(False)
        self._update()

    def combo(self) -> str:
        mods = {m for m, cb in self.checks.items() if cb.isChecked()}
        return combo_to_str(mods, self.key.currentData())

    def result(self) -> CheckResult:
        return self._check(self.combo())

    def _update(self, *_):
        c = self.combo()
        self.preview.setText(f"<span style='font-size:14pt'><b>{combo_label(c, self.fam)}</b></span>")
        self.status.setText(describe_result(self._check(c)))
        self.changed.emit(c)

    def _do_suggest(self):
        s = self._suggest()
        if s:
            self.set_combo(s)
        else:
            QtWidgets.QMessageBox.information(self, "Vorschlag",
                                              "Keine freie Standardkombination gefunden.")
