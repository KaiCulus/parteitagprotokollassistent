"""Konfliktprüfung: Ist ein Hotkey schon belegt – vom System, vom Browser, von der
Textverarbeitung oder von einem anderen Textblock in diesem Programm?"""
from __future__ import annotations

from dataclasses import dataclass, field

from .combos import combo_to_str, normalize, parse_combo
from .constants import (BROWSER_CHOICES, F_KEYS, KEY_CHOICES, LAYOUT_CHOICES,
                        OS_CHOICES, REAL_FAMILY, SYSTEM, label_for, os_family)
from .model import Block, Settings
from .shortcut_db import (ALTGR_DE_WIN, BROWSER_SHORTCUTS, OPTION_DE_MAC,
                          OS_SHORTCUTS, OS_SOURCE, PROCESSORS)


@dataclass(frozen=True)
class Shortcut:
    combo: str
    source: str
    desc: str


@dataclass
class CheckResult:
    invalid: str | None = None                                  # Hotkey unbrauchbar
    system: list[tuple[str, str]] = field(default_factory=list)  # (Quelle, Funktion)
    own: list[Block] = field(default_factory=list)              # andere Textblöcke

    @property
    def has_conflict(self) -> bool:
        return bool(self.system or self.own)


# ── Datenbank für die gewählte Umgebung ──────────────────────────────────────
def collect_shortcuts(settings: Settings) -> list[Shortcut]:
    """Alle bekannten belegten Kürzel für Betriebssystem/Textverarbeitung/Browser."""
    fam = os_family(settings.os)
    out: list[Shortcut] = []
    seen = set()

    def add(entries, source):
        for entry in entries:
            combo, desc = entry[0], entry[1]
            fams = entry[2] if len(entry) > 2 else None
            if fams and fam not in fams:
                continue
            sc = Shortcut(normalize(combo, fam), source, desc)
            if sc.combo and sc not in seen:
                seen.add(sc)
                out.append(sc)

    add(OS_SHORTCUTS[fam], OS_SOURCE[fam])
    if settings.layout == "de" and fam == "win":
        add(ALTGR_DE_WIN, "Tastatur (Strg+Alt = AltGr)")
    if settings.layout == "de" and fam == "mac":
        add(OPTION_DE_MAC, "Tastatur (Option-Zeichen)")
    name, web, entries = PROCESSORS[settings.processor]
    add(entries, name)
    if web:
        add(BROWSER_SHORTCUTS[settings.browser], label_for(BROWSER_CHOICES, settings.browser))
    return out


def build_index(shortcuts) -> dict[str, list[Shortcut]]:
    idx: dict[str, list[Shortcut]] = {}
    for sc in shortcuts:
        idx.setdefault(sc.combo, []).append(sc)
    return idx


# ── Regeln ───────────────────────────────────────────────────────────────────
def invalid_reason(mods, key) -> str | None:
    if key not in KEY_CHOICES:
        return f"Taste „{key}“ wird nicht unterstützt."
    if key not in F_KEYS and not (set(mods) - {"shift"}):
        return "Ohne STRG/ALT/WIN/CMD würde der Hotkey das normale Tippen blockieren."
    return None


def rule_conflicts(mods, key, settings: Settings) -> list[tuple[str, str]]:
    """Regelbasierte Warnungen, die in keiner Liste stehen."""
    fam = os_family(settings.os)
    mods = set(mods)
    out = []
    if fam in ("win", "linux") and mods == {"alt"} and len(key) == 1 and key.isalpha():
        out.append(("Programm-Menüs", "ALT+Buchstabe öffnet Menüs (Word, LibreOffice, Browser)"))
    if fam == "mac" and "alt" in mods and mods <= {"alt", "shift"} and key not in F_KEYS:
        out.append(("macOS-Tastatur", "Option+Taste erzeugt Sonderzeichen"))
    return out


def env_warnings(settings: Settings) -> list[str]:
    fam = os_family(settings.os)
    _, web, _ = PROCESSORS[settings.processor]
    w = []
    if settings.processor == "word" and fam == "linux":
        w.append("MS Word gibt es nicht als Linux-Programm – vermutlich ist „MS Word (Web)“ gemeint.")
    if web and settings.browser == "safari" and fam != "mac":
        w.append("Safari gibt es nur unter macOS.")
    if fam != REAL_FAMILY:
        w.append(f"Das Programm läuft gerade unter {SYSTEM}, ausgewählt ist "
                 f"{label_for(OS_CHOICES, settings.os)}. Die Konfliktprüfung richtet sich "
                 "nach der Auswahl, die Hotkeys selbst nach dem tatsächlichen System.")
    return w


def describe_env(settings: Settings) -> str:
    name, web, _ = PROCESSORS[settings.processor]
    parts = [label_for(OS_CHOICES, settings.os), name]
    if web:
        parts.append(label_for(BROWSER_CHOICES, settings.browser))
    parts.append(label_for(LAYOUT_CHOICES, settings.layout))
    return " · ".join(parts)


# ── Komfort-Klasse für die Oberfläche ────────────────────────────────────────
class ConflictChecker:
    """Prüft Hotkeys gegen die Kürzel-Datenbank und die eigenen Textblöcke."""

    def __init__(self, settings: Settings, blocks: list[Block]):
        self.settings = settings
        self.blocks = blocks
        self._cache = None

    def index(self) -> dict[str, list[Shortcut]]:
        s = self.settings
        key = (s.os, s.processor, s.browser, s.layout)
        if not self._cache or self._cache[0] != key:
            self._cache = (key, build_index(collect_shortcuts(s)))
        return self._cache[1]

    def check(self, combo: str, exclude_id: str | None = None) -> CheckResult:
        p = parse_combo(combo)
        if not p:
            return CheckResult(invalid="Kein Hotkey gewählt.")
        mods, key = p
        norm = combo_to_str(mods, key)
        res = CheckResult(invalid=invalid_reason(mods, key))
        res.system = [(sc.source, sc.desc) for sc in self.index().get(norm, [])]
        res.system += rule_conflicts(mods, key, self.settings)
        res.own = [b for b in self.blocks
                   if b.id != exclude_id and b.hotkey and normalize(b.hotkey) == norm]
        return res

    def used(self, exclude_id: str | None = None) -> set[str]:
        return {normalize(b.hotkey) for b in self.blocks if b.hotkey and b.id != exclude_id}

    def suggest(self, exclude_id: str | None = None, count: int = 1) -> list[str]:
        """Freie Kombinationen, bevorzugt STRG+SHIFT+Ziffer."""
        fam = os_family(self.settings.os)
        digits = "1234567890"
        cands = [f"ctrl+shift+{d}" for d in digits]
        cands += [f"ctrl+alt+shift+{d}" for d in digits]
        if fam == "mac":
            cands += [f"ctrl+alt+{d}" for d in digits]
        cands += [f"ctrl+shift+{k}" for k in F_KEYS]
        cands += [f"ctrl+alt+shift+{k}" for k in F_KEYS]
        cands += [f"ctrl+alt+shift+{c}" for c in "abcdefghijklmnopqrstuvwxyz"]
        index, used = self.index(), self.used(exclude_id)
        out = []
        for c in cands:
            mods, key = parse_combo(c)
            norm = combo_to_str(mods, key)
            if norm in index or norm in used or rule_conflicts(mods, key, self.settings):
                continue
            out.append(norm)
            if len(out) >= count:
                break
        return out
