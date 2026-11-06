"""Datenmodell: Einstellungen, formatierte Textstücke und Textblöcke."""
from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field

from .constants import IS_LINUX, default_os_key


@dataclass
class Settings:
    os: str = field(default_factory=default_os_key)
    processor: str = field(default_factory=lambda: "libreoffice" if IS_LINUX else "word")
    browser: str = "firefox"
    layout: str = "de"
    time_format: str = "%H:%M"
    date_format: str = "%d.%m.%Y"
    suppress: bool = True          # nur Windows: Hotkey vor dem Zielprogramm abfangen
    hotkeys_active: bool = True


@dataclass
class Run:
    """Ein gleichmäßig formatiertes Textstück."""
    text: str
    color: str | None = None       # Schriftfarbe "#rrggbb"
    bg: str | None = None          # Hintergrund / Hervorhebung
    size: float | None = None      # Schriftgröße in pt (None = wie im Zieldokument)
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False

    def fmt(self):
        return (self.color, self.bg, self.size, self.bold,
                self.italic, self.underline, self.strike)


@dataclass
class Block:
    """Ein Textblock mit Hotkey. ``lines`` ist eine Liste von Zeilen, jede Zeile eine
    Liste von :class:`Run`."""
    id: str
    hotkey: str = ""
    lines: list = field(default_factory=lambda: [[]])
    paragraphs: bool = False       # False: Zeilen per Zeilenumbruch, True: eigene Absätze
    enter_after: int = 0           # nach dem Einfügen n-mal Enter drücken


def new_id() -> str:
    return uuid.uuid4().hex[:10]


def merge_runs(runs: list[Run]) -> list[Run]:
    """Fasst benachbarte Stücke mit gleicher Formatierung zusammen."""
    out: list[Run] = []
    for r in runs:
        if not r.text:
            continue
        if out and out[-1].fmt() == r.fmt():
            out[-1] = copy.copy(out[-1])
            out[-1].text += r.text
        else:
            out.append(copy.copy(r))
    return out


def plain_text(block: Block) -> str:
    return "\n".join("".join(r.text for r in line) for line in block.lines)


def is_empty(block: Block) -> bool:
    return not plain_text(block).strip()


def block_summary(block: Block, limit: int = 45) -> str:
    """Kurzbeschreibung für Meldungen, z. B. '{{Systime}} Uhr: Redebeitrag:'."""
    text = " ".join(t for t in plain_text(block).split("\n") if t.strip()).strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def default_blocks() -> list[Block]:
    """Beispielblöcke beim allerersten Start."""
    t = "{{Systime}} Uhr:"
    return [
        Block(new_id(), "ctrl+shift+1", lines=[[Run(t + " ")]]),
        Block(new_id(), "ctrl+shift+2", lines=[[Run(t)], [Run("Redebeitrag: ")]]),
        Block(new_id(), "ctrl+shift+3", lines=[[Run(t)], [Run("Zwischenfrage: ")]]),
    ]
