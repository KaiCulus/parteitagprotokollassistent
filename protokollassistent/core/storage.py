"""Speichern und Laden der Textblöcke, Hotkeys und Einstellungen als XML.

Beispiel::

    <protokollassistent version="2">
      <einstellungen betriebssystem="windows" textverarbeitung="word" ... />
      <textbloecke>
        <textblock id="a1b2c3" hotkey="ctrl+shift+2" absaetze="nein" enter_danach="0">
          <zeile><text>{{Systime}} Uhr:</text></zeile>
          <zeile><text fett="ja">Redebeitrag:</text><text> </text></zeile>
        </textblock>
      </textbloecke>
    </protokollassistent>
"""
from __future__ import annotations

import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .combos import normalize
from .constants import (APP_NAME, BROWSER_CHOICES, IS_MAC, IS_WIN, LAYOUT_CHOICES,
                        OS_CHOICES, XML_VERSION, default_os_key)
from .model import Block, Run, Settings, merge_runs, new_id
from .placeholders import convert_legacy
from .shortcut_db import PROCESSORS

FILE_NAME = "textbloecke.xml"
ROOT_TAG = "protokollassistent"
LEGACY_ROOT_TAGS = {"protokollhelfer"}           # Vorgängerversion

SETTINGS_XML = {"os": "betriebssystem", "processor": "textverarbeitung",
                "browser": "browser", "layout": "tastaturlayout",
                "time_format": "zeitformat", "date_format": "datumsformat",
                "suppress": "hotkeys_abfangen", "hotkeys_active": "hotkeys_aktiv"}

_FLAGS = (("bold", "fett"), ("italic", "kursiv"),
          ("underline", "unterstrichen"), ("strike", "durchgestrichen"))


# ── Speicherort ──────────────────────────────────────────────────────────────
def _user_config_dir() -> Path:
    if IS_WIN:
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif IS_MAC:
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / APP_NAME


def default_config_path() -> Path:
    """Neben dem Programm (gut auffindbar, portabel), sonst im Benutzerprofil."""
    program_dir = Path(__file__).resolve().parents[2]       # Ordner mit start.py
    candidate = program_dir / FILE_NAME
    if candidate.exists() or os.access(program_dir, os.W_OK):
        return candidate
    return _user_config_dir() / FILE_NAME


# ── Hilfsfunktionen ──────────────────────────────────────────────────────────
def _b(v: bool) -> str:
    return "ja" if v else "nein"


def _parse_b(v, default=False) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in ("ja", "true", "1", "yes")


# ── Speichern ────────────────────────────────────────────────────────────────
def save_xml(path, settings: Settings, blocks: list[Block]) -> None:
    root = ET.Element(ROOT_TAG, version=XML_VERSION)
    s = ET.SubElement(root, "einstellungen")
    for attr, tag in SETTINGS_XML.items():
        v = getattr(settings, attr)
        s.set(tag, _b(v) if isinstance(v, bool) else str(v))

    bl = ET.SubElement(root, "textbloecke")
    for b in blocks:
        e = ET.SubElement(bl, "textblock", id=b.id, hotkey=b.hotkey,
                          absaetze=_b(b.paragraphs), enter_danach=str(b.enter_after))
        for line in b.lines:
            z = ET.SubElement(e, "zeile")
            for r in line:
                t = ET.SubElement(z, "text")
                t.text = r.text
                if r.color:
                    t.set("farbe", r.color)
                if r.bg:
                    t.set("hintergrund", r.bg)
                if r.size:
                    t.set("groesse", f"{r.size:g}")
                for attr, name in _FLAGS:
                    if getattr(r, attr):
                        t.set(name, "ja")
    ET.indent(root)

    # Erst in eine temporäre Datei schreiben, dann ersetzen – so geht bei einem
    # Absturz während des Speicherns nie die ganze Datei verloren.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".xml", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            ET.ElementTree(root).write(f, encoding="utf-8", xml_declaration=True)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ── Laden ────────────────────────────────────────────────────────────────────
def _load_settings(root) -> Settings:
    settings = Settings()
    s = root.find("einstellungen")
    if s is not None:
        for attr, tag in SETTINGS_XML.items():
            v = s.get(tag)
            if v is None:
                continue
            if isinstance(getattr(settings, attr), bool):
                setattr(settings, attr, _parse_b(v))
            else:
                setattr(settings, attr, v)
    # ungültige Werte auf Standard zurücksetzen
    if settings.os not in dict(OS_CHOICES):
        settings.os = default_os_key()
    if settings.processor not in PROCESSORS:
        settings.processor = Settings().processor
    if settings.browser not in dict(BROWSER_CHOICES):
        settings.browser = "firefox"
    if settings.layout not in dict(LAYOUT_CHOICES):
        settings.layout = "de"
    return settings


def _load_run(t) -> Run:
    size = t.get("groesse")
    try:
        size = float(size.replace(",", ".")) if size else None
    except ValueError:
        size = None
    r = Run(convert_legacy(t.text or ""), color=t.get("farbe"),
            bg=t.get("hintergrund"), size=size)
    for attr, name in _FLAGS:
        setattr(r, attr, _parse_b(t.get(name)))
    return r


def load_xml(path) -> tuple[Settings, list[Block]]:
    root = ET.parse(path).getroot()
    if root.tag != ROOT_TAG and root.tag not in LEGACY_ROOT_TAGS:
        raise ValueError("Keine Protokollassistent-Datei (unbekanntes Wurzelelement "
                         f"<{root.tag}>).")
    settings = _load_settings(root)

    blocks = []
    # "textblock" = aktuelles Format, "baustein" = Vorgängerversion
    for e in [*root.iter("textblock"), *root.iter("baustein")]:
        lines = [merge_runs([_load_run(t) for t in z.findall("text")])
                 for z in e.findall("zeile")]
        try:
            enter_after = max(0, min(5, int(e.get("enter_danach", "0"))))
        except ValueError:
            enter_after = 0
        blocks.append(Block(id=e.get("id") or new_id(),
                            hotkey=normalize(e.get("hotkey", "")),
                            lines=lines or [[]],
                            paragraphs=_parse_b(e.get("absaetze")),
                            enter_after=enter_after))
    return settings, blocks
