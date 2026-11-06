"""Dialog „Betriebssystem / Browser / Textverarbeitung festlegen“."""
from __future__ import annotations

import copy

from PySide6 import QtWidgets

from ..core.conflicts import ConflictChecker, env_warnings
from ..core.constants import (BROWSER_CHOICES, IS_WIN, LAYOUT_CHOICES, OS_CHOICES)
from ..core.model import Block, Settings
from ..core.placeholders import SYSTIME, placeholder_values
from ..core.shortcut_db import PROCESSOR_CHOICES, PROCESSORS
from . import theme
from .overview_dialog import OverviewDialog


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent, settings: Settings, blocks: list[Block]):
        super().__init__(parent)
        self.setWindowTitle("Betriebssystem / Browser / Textverarbeitung festlegen")
        self.settings = copy.deepcopy(settings)      # erst bei „Übernehmen“ wirksam
        self.blocks = blocks
        lay = QtWidgets.QVBoxLayout(self)

        # ── Umgebung ──
        box = QtWidgets.QGroupBox("Arbeitsumgebung (für die Warnung vor belegten Hotkeys)")
        form = QtWidgets.QFormLayout(box)
        self.os_combo = self._combo(OS_CHOICES, self.settings.os)
        self.proc_combo = self._combo(PROCESSOR_CHOICES, self.settings.processor)
        self.browser_combo = self._combo(BROWSER_CHOICES, self.settings.browser)
        self.layout_combo = self._combo(LAYOUT_CHOICES, self.settings.layout)
        form.addRow("Betriebssystem:", self.os_combo)
        form.addRow("Textverarbeitung:", self.proc_combo)
        form.addRow("Browser:", self.browser_combo)
        form.addRow("Tastaturlayout:", self.layout_combo)
        self.env_warn = QtWidgets.QLabel()
        self.env_warn.setWordWrap(True)
        self.env_warn.setStyleSheet(f"color:{theme.WARN_ORANGE}")
        form.addRow("", self.env_warn)
        b_ov = QtWidgets.QPushButton("Übersicht belegter Tastenkürzel anzeigen …")
        b_ov.clicked.connect(self._show_overview)
        form.addRow("", b_ov)
        lay.addWidget(box)

        # ── Zeitformat ──
        box2 = QtWidgets.QGroupBox("Systemzeit")
        f2 = QtWidgets.QFormLayout(box2)
        self.time_edit = QtWidgets.QLineEdit(self.settings.time_format)
        self.date_edit = QtWidgets.QLineEdit(self.settings.date_format)
        self.time_example = QtWidgets.QLabel()
        self.date_example = QtWidgets.QLabel()
        self.time_edit.textEdited.connect(self._update)
        self.date_edit.textEdited.connect(self._update)
        f2.addRow(f"Format {SYSTIME}:", self.time_edit)
        f2.addRow("", self.time_example)
        f2.addRow("Format {{Datum}}:", self.date_edit)
        f2.addRow("", self.date_example)
        hint = QtWidgets.QLabel("Kürzel: %H Stunde, %M Minute, %S Sekunde, %d Tag, %m Monat, "
                                "%Y Jahr. Beispiel: „%H:%M:%S“ → 14:07:33")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{theme.MUTED}")
        f2.addRow("", hint)
        lay.addWidget(box2)

        # ── Verhalten ──
        box3 = QtWidgets.QGroupBox("Verhalten")
        v3 = QtWidgets.QVBoxLayout(box3)
        self.suppress_check = QtWidgets.QCheckBox(
            "Hotkey vor dem Zielprogramm abfangen (nur Windows)")
        self.suppress_check.setToolTip(
            "Unter Windows bekommt das Zielprogramm die Tastenkombination dann nicht zu sehen.")
        self.suppress_check.setChecked(self.settings.suppress)
        self.suppress_check.setEnabled(IS_WIN)
        v3.addWidget(self.suppress_check)
        lay.addWidget(box3)

        SB = QtWidgets.QDialogButtonBox.StandardButton
        buttons = QtWidgets.QDialogButtonBox(SB.Ok | SB.Cancel)
        buttons.button(SB.Ok).setText("Übernehmen")
        buttons.button(SB.Cancel).setText("Abbrechen")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        lay.addWidget(buttons)

        self._update()
        self.resize(560, self.sizeHint().height())

    def _combo(self, choices, current):
        c = QtWidgets.QComboBox()
        for k, v in choices:
            c.addItem(v, k)
        c.setCurrentIndex(max(c.findData(current), 0))
        c.currentIndexChanged.connect(self._update)
        return c

    def _read(self) -> Settings:
        s = self.settings
        s.os = self.os_combo.currentData()
        s.processor = self.proc_combo.currentData()
        s.browser = self.browser_combo.currentData()
        s.layout = self.layout_combo.currentData()
        s.time_format = self.time_edit.text() or "%H:%M"
        s.date_format = self.date_edit.text() or "%d.%m.%Y"
        s.suppress = self.suppress_check.isChecked()
        return s

    def _update(self, *_):
        s = self._read()
        self.browser_combo.setEnabled(PROCESSORS[s.processor][1])     # nur bei Web-Programmen
        self.env_warn.setText("\n".join("⚠ " + w for w in env_warnings(s)))
        v = placeholder_values(s)
        self.time_example.setText(f"→ {v['SYSTIME']}")
        self.date_example.setText(f"→ {v['DATUM']}  ({v['WOCHENTAG']})")

    def _show_overview(self):
        OverviewDialog(self, ConflictChecker(self._read(), self.blocks)).exec()

    def result_settings(self) -> Settings:
        return self._read()
