"""Hotkey-Notation.

Intern wird eine Kombination als Text gespeichert, z. B. ``"ctrl+shift+1"``
(Modifikatoren in fester Reihenfolge, dann die Taste).
In der Kürzel-Datenbank darf ``mod`` stehen = Strg (Win/Linux) bzw. Cmd (macOS).
"""
from __future__ import annotations

from .constants import KEY_CHOICES, MOD_LABELS, MODIFIERS

_MOD_ALIASES = {
    "ctrl": "ctrl", "strg": "ctrl", "control": "ctrl",
    "alt": "alt", "option": "alt", "opt": "alt",
    "shift": "shift", "umschalt": "shift",
    "cmd": "cmd", "win": "cmd", "super": "cmd", "meta": "cmd", "command": "cmd",
}


def parse_combo(text: str, fam: str | None = None):
    """'STRG+SHIFT+1' / 'ctrl+shift+1' / 'mod+b' → (frozenset(mods), key) oder None."""
    if not text:
        return None
    mods, key = set(), None
    for part in (p.strip().lower() for p in text.split("+")):
        if not part:
            continue
        if part == "mod":
            mods.add("cmd" if fam == "mac" else "ctrl")
        elif part in _MOD_ALIASES:
            mods.add(_MOD_ALIASES[part])
        else:
            key = part
    if key is None:
        return None
    return frozenset(mods), key


def combo_to_str(mods, key) -> str:
    return "+".join([m for m in MODIFIERS if m in mods] + [key])


def normalize(text: str, fam: str | None = None) -> str:
    p = parse_combo(text, fam)
    return combo_to_str(*p) if p else ""


def key_label(key: str) -> str:
    return key.upper()


def combo_label(text: str, fam: str) -> str:
    """Anzeige, z. B. 'STRG+SHIFT+1'."""
    p = parse_combo(text, fam)
    if not p:
        return "–"
    mods, key = p
    names = MOD_LABELS[fam]
    return "+".join([names[m] for m in MODIFIERS if m in mods] + [key_label(key)])


def combo_sort_key(text: str):
    p = parse_combo(text)
    if not p:
        return (99,)
    mods, key = p
    k = KEY_CHOICES.index(key) if key in KEY_CHOICES else 999
    return (len(mods), tuple(MODIFIERS.index(m) for m in MODIFIERS if m in mods), k)
