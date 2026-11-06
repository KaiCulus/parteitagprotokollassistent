"""Programmweite Konstanten, Plattform-Erkennung und Auswahllisten."""
from __future__ import annotations

import os
import platform

APP_NAME = "Protokollassistent"
XML_VERSION = "2"

SYSTEM = platform.system()
IS_WIN = SYSTEM == "Windows"
IS_MAC = SYSTEM == "Darwin"
IS_LINUX = not (IS_WIN or IS_MAC)
REAL_FAMILY = "win" if IS_WIN else "mac" if IS_MAC else "linux"

# ── Auswahllisten (Schlüssel, Anzeigename) ──────────────────────────────────
OS_CHOICES = [("windows", "Windows"), ("macos", "macOS"),
              ("debian", "Debian / Ubuntu"), ("arch", "Arch Linux")]

BROWSER_CHOICES = [("firefox", "Firefox"), ("chrome", "Google Chrome"),
                   ("chromium", "Chromium"), ("edge", "Microsoft Edge"),
                   ("safari", "Safari"), ("vivaldi", "Vivaldi"), ("brave", "Brave")]

LAYOUT_CHOICES = [("de", "Deutsch (QWERTZ)"), ("us", "US-Englisch (QWERTY)")]

# ── Tasten ───────────────────────────────────────────────────────────────────
MODIFIERS = ("ctrl", "alt", "shift", "cmd")          # feste Reihenfolge
F_KEYS = [f"f{i}" for i in range(1, 13)]
KEY_CHOICES = (list("1234567890")
               + [chr(c) for c in range(ord("a"), ord("z") + 1)]
               + F_KEYS)

MOD_LABELS = {
    "win":   {"ctrl": "STRG", "alt": "ALT", "shift": "SHIFT", "cmd": "WIN"},
    "linux": {"ctrl": "STRG", "alt": "ALT", "shift": "SHIFT", "cmd": "SUPER"},
    "mac":   {"ctrl": "CTRL", "alt": "OPTION", "shift": "SHIFT", "cmd": "CMD"},
}

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
              "Freitag", "Samstag", "Sonntag"]


def os_family(os_key: str) -> str:
    """'windows' → 'win', 'macos' → 'mac', alles andere → 'linux'."""
    return {"windows": "win", "macos": "mac"}.get(os_key, "linux")


def default_os_key() -> str:
    if IS_WIN:
        return "windows"
    if IS_MAC:
        return "macos"
    return "arch" if os.path.exists("/etc/arch-release") else "debian"


def label_for(choices, key) -> str:
    return dict(choices).get(key, key)
