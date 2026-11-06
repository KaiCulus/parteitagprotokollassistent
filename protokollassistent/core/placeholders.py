"""Platzhalter wie {{Systime}} – werden beim Einfügen durch die aktuelle Zeit ersetzt."""
from __future__ import annotations

import copy
import re
from datetime import datetime

from .constants import WOCHENTAGE
from .model import Run, Settings, merge_runs

SYSTIME = "{{Systime}}"

# Groß-/Kleinschreibung egal, Leerzeichen innerhalb der Klammern erlaubt: {{ systime }}
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_]+)\s*\}\}")

PLACEHOLDERS = [
    (SYSTIME, "Aktuelle Systemzeit (z. B. 14:07)"),
    ("{{Datum}}", "Aktuelles Datum (z. B. 06.11.2026)"),
    ("{{Wochentag}}", "Wochentag (z. B. Freitag)"),
]

# Ältere Konfigurationen benutzten {SYSTEMTIME}, {UHRZEIT}, {DATUM}, {WOCHENTAG}
_LEGACY_RE = re.compile(r"(?<!\{)\{(SYSTEMTIME|UHRZEIT|DATUM|WOCHENTAG)\}(?!\})", re.I)
_LEGACY_MAP = {"SYSTEMTIME": SYSTIME, "UHRZEIT": SYSTIME,
               "DATUM": "{{Datum}}", "WOCHENTAG": "{{Wochentag}}"}


def convert_legacy(text: str) -> str:
    return _LEGACY_RE.sub(lambda m: _LEGACY_MAP[m.group(1).upper()], text)


def safe_strftime(dt: datetime, fmt: str) -> str:
    try:
        return dt.strftime(fmt)
    except (ValueError, TypeError):
        return fmt


def current_systemtime(fmt: str = "%H:%M") -> str:
    """Aktuelle Systemzeit als Text, z. B. '14:07'."""
    return safe_strftime(datetime.now(), fmt)


def placeholder_values(settings: Settings, now: datetime | None = None) -> dict[str, str]:
    now = now or datetime.now()
    t = safe_strftime(now, settings.time_format)
    return {"SYSTIME": t, "SYSTEMTIME": t, "UHRZEIT": t, "ZEIT": t,
            "DATUM": safe_strftime(now, settings.date_format),
            "WOCHENTAG": WOCHENTAGE[now.weekday()]}


def expand_line(runs: list[Run], values: dict[str, str]) -> list[Run]:
    """Ersetzt Platzhalter – auch wenn sie über mehrere Formatierungen verteilt sind.
    Der Ersatztext übernimmt die Formatierung des ersten Platzhalter-Zeichens."""
    text = "".join(r.text for r in runs)
    owner = [i for i, r in enumerate(runs) for _ in r.text]
    pieces: list[Run] = []
    i = 0
    while i < len(text):
        m = PLACEHOLDER_RE.match(text, i)
        if m and m.group(1).upper() in values:
            r = copy.copy(runs[owner[i]])
            r.text = values[m.group(1).upper()]
            pieces.append(r)
            i = m.end()
        else:
            r = copy.copy(runs[owner[i]])
            r.text = text[i]
            pieces.append(r)
            i += 1
    return merge_runs(pieces)
