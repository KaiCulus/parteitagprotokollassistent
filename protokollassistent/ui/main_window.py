"""Hauptfenster: Buttons oben, Tabelle der Hotkeys, automatisches Speichern als XML."""
from __future__ import annotations

import os
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from ..core.combos import combo_to_str, parse_combo
from ..core.conflicts import ConflictChecker, invalid_reason
from ..core.constants import APP_NAME, IS_LINUX, IS_MAC, IS_WIN
from ..core.model import Block, Settings, block_summary, default_blocks
from ..core.placeholders import current_systemtime
from ..core.render import render_block
from ..core.storage import default_config_path, load_xml, save_xml
from ..system import hotkey_engine
from ..system.clipboard import set_clipboard
from ..system.hotkey_engine import HotkeyEngine
from . import theme
from .block_dialog import BlockDialog
from .block_table import BlockTable
from .settings_dialog import SettingsDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config_path: Path | None = None):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 560)
        self.qsettings = QtCore.QSettings(APP_NAME, APP_NAME)
        self.config_path = Path(config_path) if config_path else self._initial_path()
        self.settings = Settings()
        self.blocks: list[Block] = []
        self.checker = ConflictChecker(self.settings, self.blocks)

        self.engine = HotkeyEngine()
        self.engine.triggered.connect(self._on_hotkey)

        self._build_ui()
        self._load()
        QtCore.QTimer.singleShot(0, self._startup_checks)

    # ────────────────────────────── Aufbau ──────────────────────────────
    def _build_ui(self):
        menu = self.menuBar().addMenu("&Datei")
        menu.addAction("Andere XML-Datei öffnen …", self._open_other)
        menu.addAction("Kopie speichern unter …", self._save_copy)
        menu.addSeparator()
        menu.addAction("Speicherort anzeigen", self._show_location)
        menu.addSeparator()
        menu.addAction("Beenden", self.close)

        central = QtWidgets.QWidget()
        central.setStyleSheet("background:white;")
        self.setCentralWidget(central)
        lay = QtWidgets.QVBoxLayout(central)
        lay.setContentsMargins(40, 30, 40, 20)
        lay.setSpacing(40)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(60)
        b_new = QtWidgets.QPushButton("Neuer Hotkey")
        b_env = QtWidgets.QPushButton("Betriebssystem / Browser /Textverarbeitung festlegen")
        for b in (b_new, b_env):
            b.setStyleSheet(theme.PRIMARY_BUTTON)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            top.addWidget(b)
        b_new.clicked.connect(self._new_block)
        b_env.clicked.connect(self._edit_settings)
        top.addStretch()
        lay.addLayout(top)

        self.table = BlockTable()
        self.table.editRequested.connect(self._edit_block)
        self.table.deleteRequested.connect(self._delete_block)
        lay.addWidget(self.table, 1)

        # Statusleiste: Hotkeys an/aus + Speicherort
        sb = self.statusBar()
        self.active_check = QtWidgets.QCheckBox("Hotkeys aktiv")
        self.active_check.toggled.connect(self._toggle_active)
        sb.addPermanentWidget(self.active_check)
        self.path_label = QtWidgets.QLabel()
        self.path_label.setStyleSheet(f"color:{theme.MUTED}")
        sb.addPermanentWidget(self.path_label)

    # ────────────────────────────── Laden / Speichern ──────────────────────────────
    def _initial_path(self) -> Path:
        last = self.qsettings.value("config_file", "")
        if last and Path(last).exists():
            return Path(last)
        return default_config_path()

    def _load(self):
        if self.config_path.exists():
            try:
                self.settings, self.blocks = load_xml(self.config_path)
            except Exception as exc:
                QtWidgets.QMessageBox.critical(
                    self, APP_NAME,
                    f"Die Datei\n{self.config_path}\nkonnte nicht gelesen werden:\n{exc}\n\n"
                    "Es wird mit Beispiel-Textblöcken gestartet; die Datei wird erst "
                    "beim nächsten Speichern überschrieben.")
                self.settings, self.blocks = Settings(), default_blocks()
        else:
            self.settings, self.blocks = Settings(), default_blocks()
            self._save()
        self._after_load()

    def _after_load(self):
        self.checker = ConflictChecker(self.settings, self.blocks)
        self.engine.layout = self.settings.layout
        self.engine.suppress = self.settings.suppress
        self.active_check.blockSignals(True)
        self.active_check.setChecked(self.settings.hotkeys_active)
        self.active_check.blockSignals(False)
        self.path_label.setText(f"Gespeichert in: {self.config_path}")
        self._refresh()

    def _save(self) -> bool:
        """Automatisches Speichern nach jeder Änderung."""
        try:
            save_xml(self.config_path, self.settings, self.blocks)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(
                self, APP_NAME, f"Speichern nach {self.config_path} fehlgeschlagen:\n{exc}")
            return False
        self.qsettings.setValue("config_file", str(self.config_path))
        return True

    def _open_other(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "XML-Datei öffnen", str(self.config_path.parent), "XML-Datei (*.xml)")
        if not path:
            return
        try:
            settings, blocks = load_xml(path)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, APP_NAME, f"Datei konnte nicht gelesen werden:\n{exc}")
            return
        self.config_path = Path(path)
        self.settings, self.blocks = settings, blocks
        self.qsettings.setValue("config_file", path)
        self._after_load()
        self._restart_engine_if_needed()

    def _save_copy(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Kopie speichern unter", str(self.config_path), "XML-Datei (*.xml)")
        if not path:
            return
        if not path.lower().endswith(".xml"):
            path += ".xml"
        try:
            save_xml(path, self.settings, self.blocks)
        except Exception as exc:
            QtWidgets.QMessageBox.critical(self, APP_NAME, f"Speichern fehlgeschlagen:\n{exc}")
            return
        self.statusBar().showMessage(f"Kopie gespeichert: {path}", 5000)

    def _show_location(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(self.config_path.parent)))

    # ────────────────────────────── Anzeige ──────────────────────────────
    def block(self, bid) -> Block | None:
        return next((b for b in self.blocks if b.id == bid), None)

    def _refresh(self):
        self.table.set_blocks(self.blocks, self.checker)
        self._register_hotkeys()

    def _register_hotkeys(self):
        mapping = {}
        for b in self.blocks:
            p = parse_combo(b.hotkey)
            if not p or invalid_reason(*p):
                continue
            mapping.setdefault(combo_to_str(*p), b.id)
        self.engine.set_hotkeys(mapping)

    # ────────────────────────────── Textblöcke ──────────────────────────────
    def _new_block(self):
        dlg = BlockDialog(self, None, self.checker, self.settings)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._apply_dialog(dlg, new=True)

    def _edit_block(self, bid):
        b = self.block(bid)
        if b is None:
            return
        dlg = BlockDialog(self, b, self.checker, self.settings)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self._apply_dialog(dlg, new=False)

    def _apply_dialog(self, dlg: BlockDialog, new: bool):
        result = dlg.result_block()
        # Überschreiben: andere Textblöcke verlieren diesen Hotkey
        for other in self.blocks:
            if other.id in dlg.overwritten_ids:
                other.hotkey = ""
        if new:
            self.blocks.append(result)
        else:
            i = next(i for i, b in enumerate(self.blocks) if b.id == result.id)
            self.blocks[i] = result
        self._save()
        self._refresh()
        msg = "Hotkey angelegt" if new else "Änderungen gespeichert"
        if dlg.overwritten_ids:
            msg += " – bisherige Zuweisung wurde überschrieben"
        self.statusBar().showMessage(msg, 5000)

    def _delete_block(self, bid):
        b = self.block(bid)
        if b is None:
            return
        r = QtWidgets.QMessageBox.question(
            self, "Löschen", f"Textblock „{block_summary(b)}“ wirklich löschen?")
        if r != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.blocks.remove(b)
        self._save()
        self._refresh()

    # ────────────────────────────── Einstellungen ──────────────────────────────
    def _edit_settings(self):
        dlg = SettingsDialog(self, self.settings, self.blocks)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return
        new = dlg.result_settings()
        suppress_changed = new.suppress != self.settings.suppress
        # Werte übernehmen (gleiches Objekt behalten – der ConflictChecker hält es)
        for field in vars(new):
            setattr(self.settings, field, getattr(new, field))
        self.engine.layout = self.settings.layout
        self.engine.suppress = self.settings.suppress
        if suppress_changed and self.engine.running:
            self._start_engine()
        self._save()
        self._refresh()

    # ────────────────────────────── Hotkeys ──────────────────────────────
    def _startup_checks(self):
        msgs = []
        if not hotkey_engine.available():
            msgs.append("Das Modul „pynput“ konnte nicht geladen werden – globale Hotkeys sind "
                        "deaktiviert. Installation: pip install pynput\n"
                        f"({hotkey_engine.PYNPUT_ERROR})")
            self.active_check.setEnabled(False)
        if IS_LINUX and os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland":
            msgs.append("Du nutzt eine Wayland-Sitzung. Globale Hotkeys und das automatische "
                        "Einfügen funktionieren dort nur eingeschränkt. Besser beim Login eine "
                        "X11-Sitzung wählen („GNOME on Xorg“ bzw. „Plasma (X11)“).")
        if msgs:
            QtWidgets.QMessageBox.warning(self, APP_NAME, "\n\n".join(msgs))
        if IS_MAC:
            self.statusBar().showMessage(
                "macOS: Falls Hotkeys nicht reagieren → Bedienungshilfen und "
                "Eingabeüberwachung für Terminal/Python erlauben.", 15000)
        self._restart_engine_if_needed()

    def _restart_engine_if_needed(self):
        if self.settings.hotkeys_active and hotkey_engine.available():
            self._start_engine()
        else:
            self.engine.stop()

    def _start_engine(self):
        try:
            self.engine.start()
            self.statusBar().showMessage(f"Hotkeys aktiv: {self.engine.count}", 4000)
        except Exception as exc:
            self.active_check.blockSignals(True)
            self.active_check.setChecked(False)
            self.active_check.blockSignals(False)
            QtWidgets.QMessageBox.warning(self, APP_NAME,
                                          f"Globale Hotkeys konnten nicht gestartet werden:\n{exc}")

    def _toggle_active(self, on):
        self.settings.hotkeys_active = on
        if on:
            self._start_engine()
        else:
            self.engine.stop()
            self.statusBar().showMessage("Hotkeys pausiert", 4000)
        self._save()

    def _on_hotkey(self, bid):
        b = self.block(bid)
        if b is None:
            return
        if QtWidgets.QApplication.activeWindow() is not None:
            # Nicht in das eigene Fenster einfügen – so lassen sich Hotkeys gefahrlos testen
            self.statusBar().showMessage(
                f"Hotkey erkannt („{block_summary(b)}“) – nicht eingefügt, weil der "
                "Protokollassistent im Vordergrund ist.", 5000)
            return
        set_clipboard(*render_block(b, self.settings))
        p = parse_combo(b.hotkey)
        mods = p[0] if p else frozenset()
        mask = IS_WIN and self.settings.suppress and bool({"alt", "cmd"} & set(mods))
        self.engine.paste(b.enter_after, mask_menu=mask)
        self.statusBar().showMessage(
            f"{current_systemtime('%H:%M:%S')}  eingefügt: {block_summary(b)}", 5000)

    def closeEvent(self, ev):
        self.engine.stop()
        ev.accept()
