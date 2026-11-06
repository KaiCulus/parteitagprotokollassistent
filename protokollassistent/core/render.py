"""Textblock → HTML (für die Zwischenablage) und Nur-Text."""
from __future__ import annotations

import html
from datetime import datetime

from .model import Block, Run, Settings
from .placeholders import PLACEHOLDER_RE, expand_line, placeholder_values

PLACEHOLDER_COLOR = "#2f2fd0"     # Hervorhebung von {{Systime}} in der Tabelle


def _escape(text: str, first: bool, last: bool) -> str:
    t = html.escape(text, quote=False)
    t = t.replace("\t", "&nbsp;" * 4).replace("  ", " &nbsp;")
    if first and t.startswith(" "):
        t = "&nbsp;" + t[1:]
    if last and t.endswith(" "):
        t = t[:-1] + "&nbsp;"          # sonst schneiden Programme das Leerzeichen ab
    return t


def _highlight_placeholders(text: str, first: bool, last: bool) -> str:
    out, pos = [], 0
    for m in PLACEHOLDER_RE.finditer(text):
        out.append(_escape(text[pos:m.start()], first and pos == 0, False))
        out.append(f'<span style="color:{PLACEHOLDER_COLOR}">{html.escape(m.group(0))}</span>')
        pos = m.end()
    out.append(_escape(text[pos:], first and pos == 0, last))
    return "".join(out)


def run_html(r: Run, first: bool, last: bool, highlight: bool = False) -> str:
    t = _highlight_placeholders(r.text, first, last) if highlight else _escape(r.text, first, last)
    if r.strike:
        t = f"<s>{t}</s>"
    if r.underline:
        t = f"<u>{t}</u>"
    if r.italic:
        t = f"<i>{t}</i>"
    if r.bold:
        t = f"<b>{t}</b>"
    style = []
    if r.color:
        style.append(f"color:{r.color}")
    if r.bg:
        style.append(f"background-color:{r.bg}")
    if r.size:
        style.append(f"font-size:{r.size:g}pt")
    if style:
        t = f'<span style="{";".join(style)}">{t}</span>'
    return t


def _lines_html(lines, highlight: bool) -> list[str]:
    return ["".join(run_html(r, i == 0, i == len(line) - 1, highlight)
                    for i, r in enumerate(line))
            for line in lines]


def render_block(block: Block, settings: Settings, now: datetime | None = None):
    """→ (html, nur_text) mit eingesetzter Systemzeit – so wie es eingefügt wird."""
    values = placeholder_values(settings, now)
    lines = [expand_line(line, values) for line in block.lines]
    html_lines = _lines_html(lines, highlight=False)
    if block.paragraphs:
        body = "".join(f'<p style="margin:0">{h or "<br>"}</p>' for h in html_lines)
    else:
        body = "<br>".join(html_lines)
    text = "\n".join("".join(r.text for r in line) for line in lines)
    return '<meta charset="utf-8">' + body, text


def render_template_html(block: Block) -> str:
    """Vorlage mit sichtbaren, blau markierten Platzhaltern (für die Tabelle)."""
    return "<br>".join(_lines_html(block.lines, highlight=True))
