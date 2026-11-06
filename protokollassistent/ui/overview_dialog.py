"""Übersicht bekannter, bereits belegter Tastenkürzel für die gewählte Umgebung."""
from __future__ import annotations

import csv
import html

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt

from ..core.combos import combo_label, combo_sort_key, normalize
from ..core.conflicts import ConflictChecker, collect_shortcuts, describe_env
from ..core.constants import os_family
from ..core.model import block_summary
from . import theme


class OverviewDialog(QtWidgets.QDialog):
    def __init__(self, parent, checker: ConflictChecker):
        super().__init__(parent)
        self.checker = checker
        s = checker.settings
        self.fam = os_family(s.os)
        self.setWindowTitle("Übersicht belegter Tastenkürzel")
        self.resize(900, 680)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(QtWidgets.QLabel(f"<b>Umgebung:</b> {html.escape(describe_env(s))}"))

        # Eigene Hotkeys
        lay.addWidget(QtWidgets.QLabel("<b>Deine Hotkeys</b>"))
        self.own = QtWidgets.QTableWidget(0, 3)
        self.own.setHorizontalHeaderLabels(["Hotkey", "Textblock", "Status"])
        self.own.verticalHeader().setVisible(False)
        self.own.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.own_rows = []
        for b in checker.blocks:
            if not b.hotkey:
                continue
            res = checker.check(b.hotkey, b.id)
            if res.invalid:
                status = "✖ " + res.invalid
            elif res.has_conflict:
                status = "⚠ " + "; ".join(
                    [f"{src}: {d}" for src, d in res.system]
                    + [f"auch Textblock „{block_summary(x)}“" for x in res.own])
            else:
                status = "✔ frei"
            self.own_rows.append((combo_label(b.hotkey, self.fam), block_summary(b), status))
            r = self.own.rowCount()
            self.own.insertRow(r)
            for c, val in enumerate(self.own_rows[-1]):
                item = QtWidgets.QTableWidgetItem(val)
                item.setToolTip(val)
                self.own.setItem(r, c, item)
        self.own.resizeColumnsToContents()
        self.own.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.own.setMaximumHeight(170)
        lay.addWidget(self.own)

        sugg = checker.suggest(count=12)
        sug = QtWidgets.QLabel("<b>Freie Vorschläge:</b> "
                               + ", ".join(combo_label(c, self.fam) for c in sugg))
        sug.setWordWrap(True)
        sug.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(sug)

        # Alle bekannten Kürzel
        lay.addWidget(QtWidgets.QLabel("<b>Bekannte belegte Tastenkürzel</b>"))
        frow = QtWidgets.QHBoxLayout()
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("Filtern (z. B. „STRG+SHIFT“, „Fett“, „Firefox“) …")
        self.search.textChanged.connect(self._filter)
        self.only_mine = QtWidgets.QCheckBox("Nur Konflikte mit meinen Hotkeys")
        self.only_mine.toggled.connect(self._filter)
        frow.addWidget(self.search, 1)
        frow.addWidget(self.only_mine)
        lay.addLayout(frow)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Tastenkürzel", "Quelle", "Funktion"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        mine = {normalize(b.hotkey) for b in checker.blocks if b.hotkey}
        self.rows = []
        for sc in sorted(collect_shortcuts(s), key=lambda x: (combo_sort_key(x.combo), x.source)):
            is_mine = sc.combo in mine
            vals = (combo_label(sc.combo, self.fam), sc.source, sc.desc)
            self.rows.append((vals, is_mine))
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in enumerate(vals):
                item = QtWidgets.QTableWidgetItem(val)
                if is_mine:
                    item.setBackground(QtGui.QColor("#ffd8a8"))
                    item.setForeground(QtGui.QColor("#000000"))
                    item.setToolTip("Kollidiert mit einem deiner Hotkeys")
                self.table.setItem(r, c, item)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.table, 1)

        note = QtWidgets.QLabel(
            "Die Liste enthält häufige Standardkürzel und ist nicht vollständig. Makros, "
            "Add-ons und eigene Desktop-Einstellungen können weitere Kürzel belegen.")
        note.setWordWrap(True)
        note.setStyleSheet(f"color:{theme.MUTED}")
        lay.addWidget(note)

        btns = QtWidgets.QHBoxLayout()
        exp = QtWidgets.QPushButton("Als CSV exportieren …")
        exp.clicked.connect(self._export)
        close = QtWidgets.QPushButton("Schließen")
        close.clicked.connect(self.accept)
        btns.addWidget(exp)
        btns.addStretch()
        btns.addWidget(close)
        lay.addLayout(btns)

    def _filter(self, *_):
        q = self.search.text().strip().lower()
        only = self.only_mine.isChecked()
        for r, (vals, is_mine) in enumerate(self.rows):
            hide = (only and not is_mine) or (q and q not in " ".join(vals).lower())
            self.table.setRowHidden(r, bool(hide))

    def _export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Übersicht exportieren", "hotkey_uebersicht.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Umgebung", describe_env(self.checker.settings)])
            w.writerow([])
            w.writerow(["Eigene Hotkeys"])
            w.writerow(["Hotkey", "Textblock", "Status"])
            w.writerows(self.own_rows)
            w.writerow([])
            w.writerow(["Bekannte belegte Kürzel"])
            w.writerow(["Tastenkürzel", "Quelle", "Funktion", "Konflikt"])
            for vals, is_mine in self.rows:
                w.writerow(list(vals) + (["JA"] if is_mine else [""]))
