"""Tabelle der Hotkeys mit Textblock-Vorschau und den Knöpfen Ändern / Löschen."""
from __future__ import annotations

import html

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal

from ..core.combos import combo_label
from ..core.conflicts import ConflictChecker
from ..core.constants import os_family
from ..core.model import Block, block_summary
from ..core.render import render_template_html
from . import theme

COL_HOTKEY, COL_TEXT, COL_ACTIONS = range(3)


class BlockTable(QtWidgets.QTableWidget):
    editRequested = Signal(str)       # Block-ID
    deleteRequested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(0, 3, parent)
        self.setHorizontalHeaderLabels(["Hotkey", "Textblock", ""])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setWordWrap(True)
        self.setStyleSheet(theme.TABLE)
        h = self.horizontalHeader()
        h.setSectionResizeMode(COL_HOTKEY, QtWidgets.QHeaderView.ResizeMode.Fixed)
        h.setSectionResizeMode(COL_TEXT, QtWidgets.QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(COL_ACTIONS, QtWidgets.QHeaderView.ResizeMode.Fixed)
        h.setHighlightSections(False)
        self.setColumnWidth(COL_HOTKEY, 170)
        self.setColumnWidth(COL_ACTIONS, 240)
        self.cellDoubleClicked.connect(self._on_double_click)
        self._ids: list[str] = []

    def set_blocks(self, blocks: list[Block], checker: ConflictChecker) -> None:
        fam = os_family(checker.settings.os)
        self.setRowCount(0)
        self._ids = [b.id for b in blocks]
        for row, b in enumerate(blocks):
            self.insertRow(row)

            # Hotkey (mit Warnsymbol bei bekannten Konflikten)
            label = combo_label(b.hotkey, fam) if b.hotkey else "– kein Hotkey –"
            item = QtWidgets.QTableWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if b.hotkey:
                res = checker.check(b.hotkey, b.id)
                if res.invalid or res.has_conflict:
                    item.setText(label + "  ⚠")
                    tips = [res.invalid] if res.invalid else []
                    tips += [f"{s}: {d}" for s, d in res.system]
                    tips += [f"Auch Textblock „{block_summary(x)}“" for x in res.own]
                    item.setToolTip("Bereits belegt:\n" + "\n".join(tips))
            self.setItem(row, COL_HOTKEY, item)

            # Textblock-Vorschau mit blau markiertem {{Systime}}
            self.setItem(row, COL_TEXT, QtWidgets.QTableWidgetItem())
            text = QtWidgets.QLabel(render_template_html(b) or "<i>(leer)</i>")
            text.setTextFormat(Qt.TextFormat.RichText)
            text.setWordWrap(True)
            text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            text.setStyleSheet("background:transparent; color:black; padding:8px 12px;"
                               " font-size:11pt;")
            text.setToolTip(html.escape(block_summary(b, 200)))
            text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.setCellWidget(row, COL_TEXT, text)

            # Ändern / Löschen
            self.setItem(row, COL_ACTIONS, QtWidgets.QTableWidgetItem())
            cell = QtWidgets.QWidget()
            cell.setStyleSheet("background:transparent;")
            lay = QtWidgets.QHBoxLayout(cell)
            lay.setContentsMargins(16, 8, 16, 8)
            lay.setSpacing(20)
            edit = QtWidgets.QPushButton("Ändern")
            edit.setStyleSheet(theme.EDIT_BUTTON)
            edit.setCursor(Qt.CursorShape.PointingHandCursor)
            edit.clicked.connect(lambda _=False, bid=b.id: self.editRequested.emit(bid))
            delete = QtWidgets.QPushButton("Löschen")
            delete.setStyleSheet(theme.DELETE_BUTTON)
            delete.setCursor(Qt.CursorShape.PointingHandCursor)
            delete.clicked.connect(lambda _=False, bid=b.id: self.deleteRequested.emit(bid))
            lay.addWidget(edit)
            lay.addWidget(delete)
            self.setCellWidget(row, COL_ACTIONS, cell)

        self.resizeRowsToContents()
        for row in range(self.rowCount()):
            self.setRowHeight(row, max(self.rowHeight(row), 74))

    def _on_double_click(self, row, _col):
        if 0 <= row < len(self._ids):
            self.editRequested.emit(self._ids[row])
