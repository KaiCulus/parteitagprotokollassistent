"""Formatierten Text (HTML + Nur-Text) in die Zwischenablage legen."""
from __future__ import annotations

from PySide6 import QtCore, QtGui


def set_clipboard(html: str, text: str) -> None:
    md = QtCore.QMimeData()
    md.setHtml(html)
    md.setText(text)
    QtGui.QGuiApplication.clipboard().setMimeData(md)
