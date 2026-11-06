"""Farben und Stylesheets – an einer Stelle, damit das Aussehen leicht anpassbar ist."""
from __future__ import annotations

BLUE = "#1063a8"
BLUE_HOVER = "#0d548f"
YELLOW = "#ffde59"
YELLOW_HOVER = "#f2cf3c"
RED = "#ff3131"
RED_HOVER = "#e02424"
OK_GREEN = "#2e7d32"
WARN_ORANGE = "#d35400"
ERROR_RED = "#c00000"
MUTED = "#777777"
PLACEHOLDER_BLUE = "#2f2fd0"

# Farbvorlagen im Editor
TEXT_COLORS = [("Schwarz", "#000000"), ("Dunkelgrau", "#595959"), ("Rot", "#c00000"),
               ("Orange", "#e26b0a"), ("Grün", "#2e7d32"), ("Blau", "#1f4e9c"),
               ("Lila", "#7030a0")]
HIGHLIGHT_COLORS = [("Gelb", "#ffff00"), ("Hellgrün", "#c6efce"), ("Türkis", "#bde5f8"),
                    ("Rosa", "#ffc7ce"), ("Hellgrau", "#e7e6e6")]
FONT_SIZES = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "36"]


def _button(bg: str, hover: str, fg: str, pad: str) -> str:
    return (f"QPushButton {{ background:{bg}; color:{fg}; border:none; padding:{pad};"
            f" font-size:11pt; }}"
            f"QPushButton:hover {{ background:{hover}; }}"
            f"QPushButton:disabled {{ background:#c8c8c8; color:#666; }}")


PRIMARY_BUTTON = _button(BLUE, BLUE_HOVER, "white", "14px 28px")
EDIT_BUTTON = _button(YELLOW, YELLOW_HOVER, "black", "8px 14px")
DELETE_BUTTON = _button(RED, RED_HOVER, "white", "8px 14px")

TABLE = """
QTableWidget { background:white; color:black; gridline-color:black;
               border:2px solid black; font-size:11pt; }
QHeaderView::section { background:white; color:black; font-weight:bold; font-size:11pt;
                       border:none; border-right:2px solid black;
                       border-bottom:2px solid black; padding:14px; }
QHeaderView::section:last { border-right:none; }
QTableWidget::item { padding:6px; }
QTableWidget::item:selected { background:#e8f0fa; color:black; }
"""
