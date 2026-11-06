"""Dialog „Neuer Hotkey“ / „Ändern“: Hotkey wählen und Textblock formatiert bearbeiten."""
from __future__ import annotations

import copy
import html

from PySide6 import QtCore, QtWidgets

from ..core.combos import combo_label
from ..core.conflicts import ConflictChecker
from ..core.constants import os_family
from ..core.model import Block, Settings, block_summary, is_empty, new_id
from ..core.placeholders import SYSTIME
from ..core.render import render_block
from . import theme
from .format_toolbar import FormatToolbar
from .hotkey_input import HotkeyInput
from .rich_text import BlockEditor


class BlockDialog(QtWidgets.QDialog):
    def __init__(self, parent, block: Block | None, checker: ConflictChecker,
                 settings: Settings):
        super().__init__(parent)
        self.is_new = block is None
        self.block = copy.deepcopy(block) if block else Block(new_id())
        self.checker = checker
        self.settings = settings
        self.fam = os_family(settings.os)
        self.overwritten_ids: list[str] = []

        self.setWindowTitle("Neuer Hotkey" if self.is_new else "Hotkey / Textblock ändern")
        self.resize(820, 640)
        lay = QtWidgets.QVBoxLayout(self)

        # ── Hotkey ──
        box_hk = QtWidgets.QGroupBox("Hotkey")
        hl = QtWidgets.QVBoxLayout(box_hk)
        self.hotkey = HotkeyInput(
            self.fam,
            check=lambda c: self.checker.check(c, self.block.id),
            suggest=lambda: next(iter(self.checker.suggest(self.block.id)), None))
        hl.addWidget(self.hotkey)
        lay.addWidget(box_hk)

        # ── Textblock ──
        box_tx = QtWidgets.QGroupBox("Textblock")
        tl = QtWidgets.QVBoxLayout(box_tx)
        self.editor = BlockEditor()
        self.toolbar = FormatToolbar(self.editor)
        tl.addWidget(self.toolbar)
        tl.addWidget(self.editor, 1)
        hint = QtWidgets.QLabel(
            f"Text markieren und formatieren. <b>{SYSTIME}</b> wird beim Einfügen durch die "
            "aktuelle Systemzeit ersetzt. ENTER erzeugt eine neue Zeile.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{theme.MUTED}")
        tl.addWidget(hint)

        opts = QtWidgets.QHBoxLayout()
        opts.addWidget(QtWidgets.QLabel("Neue Zeile im Textblock wird zu:"))
        self.rb_br = QtWidgets.QRadioButton("Zeilenumbruch")
        self.rb_p = QtWidgets.QRadioButton("neuem Absatz")
        self.rb_br.setToolTip("Wie Umschalt+Enter in Word/Docs – gut zum Einfügen mitten im Text")
        self.rb_p.setToolTip("Jede Zeile wird ein eigener Absatz")
        opts.addWidget(self.rb_br)
        opts.addWidget(self.rb_p)
        opts.addSpacing(20)
        opts.addWidget(QtWidgets.QLabel("Nach dem Einfügen Enter drücken:"))
        self.enter_spin = QtWidgets.QSpinBox()
        self.enter_spin.setRange(0, 5)
        self.enter_spin.setSuffix(" ×")
        opts.addWidget(self.enter_spin)
        opts.addStretch()
        tl.addLayout(opts)
        lay.addWidget(box_tx, 3)

        # ── Vorschau ──
        box_pv = QtWidgets.QGroupBox("Vorschau – so wird der Text jetzt eingefügt")
        pl = QtWidgets.QVBoxLayout(box_pv)
        self.preview = QtWidgets.QTextBrowser()
        self.preview.setMaximumHeight(110)
        pl.addWidget(self.preview)
        lay.addWidget(box_pv, 1)

        # ── Buttons ──
        SB = QtWidgets.QDialogButtonBox.StandardButton
        self.buttons = QtWidgets.QDialogButtonBox(SB.Save | SB.Cancel)
        self.buttons.button(SB.Save).setText("Speichern")
        self.buttons.button(SB.Cancel).setText("Abbrechen")
        self.buttons.accepted.connect(self._on_accept)
        self.buttons.rejected.connect(self.reject)
        lay.addWidget(self.buttons)

        # ── Werte setzen ──
        if self.is_new:
            self.block.lines = [[]]
        self.editor.set_lines(self.block.lines)
        self.rb_p.setChecked(self.block.paragraphs)
        self.rb_br.setChecked(not self.block.paragraphs)
        self.enter_spin.setValue(self.block.enter_after)
        start = self.block.hotkey or next(iter(checker.suggest(self.block.id)), "ctrl+shift+1")
        self.hotkey.changed.connect(self._on_hotkey_changed)
        self.hotkey.set_combo(start)

        self._timer = QtCore.QTimer(self, singleShot=True, interval=200)
        self._timer.timeout.connect(self._update_preview)
        self.editor.textChanged.connect(self._timer.start)
        self.rb_p.toggled.connect(self._timer.start)
        # Vorschau jede Sekunde aktualisieren, damit die Uhrzeit stimmt
        self._clock = QtCore.QTimer(self, interval=1000)
        self._clock.timeout.connect(self._update_preview)
        self._clock.start()
        self._update_preview()

        if self.is_new:
            self.editor.insertPlainText(SYSTIME + " Uhr: ")
        self.editor.setFocus()

    # ── Ergebnis ──
    def _collect(self) -> Block:
        b = self.block
        b.hotkey = self.hotkey.combo()
        b.lines = self.editor.lines()
        b.paragraphs = self.rb_p.isChecked()
        b.enter_after = self.enter_spin.value()
        return b

    def result_block(self) -> Block:
        return self._collect()

    # ── Ereignisse ──
    def _on_hotkey_changed(self, _combo):
        ok = self.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Save)
        ok.setEnabled(self.hotkey.result().invalid is None)

    def _update_preview(self):
        html_s, _ = render_block(self._collect(), self.settings)
        self.preview.setHtml(html_s)

    def _on_accept(self):
        b = self._collect()
        if is_empty(b):
            QtWidgets.QMessageBox.warning(self, self.windowTitle(),
                                          "Der Textblock ist leer. Bitte Text eingeben.")
            return
        res = self.checker.check(b.hotkey, b.id)
        if res.invalid:
            QtWidgets.QMessageBox.warning(self, self.windowTitle(), res.invalid)
            return
        if res.has_conflict and not self._confirm_overwrite(b.hotkey, res):
            return
        self.overwritten_ids = [x.id for x in res.own]
        self.accept()

    def _confirm_overwrite(self, combo, res) -> bool:
        label = html.escape(combo_label(combo, self.fam))
        parts = [f"Der Hotkey <b>{label}</b> ist bereits belegt:"]
        if res.own:
            items = "".join(f"<li>Textblock „{html.escape(block_summary(x))}“</li>"
                            for x in res.own)
            parts.append(f"<p><b>In diesem Programm</b> – dieser Textblock verliert seinen "
                         f"Hotkey:</p><ul>{items}</ul>")
        if res.system:
            items = "".join(f"<li><b>{html.escape(s)}</b>: {html.escape(d)}</li>"
                            for s, d in res.system)
            parts.append("<p><b>Im System / Programm</b> – diese Funktion ist dann per "
                         f"Tastatur nicht mehr nutzbar:</p><ul>{items}</ul>")
        parts.append("<p>Bestehende Belegung überschreiben?</p>")

        box = QtWidgets.QMessageBox(self)
        box.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        box.setWindowTitle("Hotkey überschreibt eine bestehende Belegung")
        box.setTextFormat(QtCore.Qt.TextFormat.RichText)
        box.setText("".join(parts))
        yes = box.addButton("Überschreiben", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        no = box.addButton("Anderen Hotkey wählen", QtWidgets.QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(no)
        box.exec()
        return box.clickedButton() is yes
