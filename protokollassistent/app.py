"""Einstiegspunkt: QApplication erzeugen und Hauptfenster anzeigen."""
from __future__ import annotations

import sys


def main() -> None:
    try:
        from PySide6 import QtWidgets
    except ImportError:  # pragma: no cover
        sys.exit("PySide6 fehlt. Installation:  pip install -r requirements.txt")

    from .core.constants import APP_NAME
    from .ui.main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
