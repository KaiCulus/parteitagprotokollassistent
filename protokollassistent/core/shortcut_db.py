"""Datenbank bekannter Tastenkürzel (Betriebssysteme, Browser, Textverarbeitungen).

Einträge: (kombination, beschreibung[, nur_für_systeme])
Bewusst nur Kombinationen mit Buchstaben, Ziffern und F-Tasten – nur diese
können im Programm als Hotkey gewählt werden. Die Liste ist nicht vollständig.
"""
from __future__ import annotations

from .combos import key_label
from .constants import F_KEYS

W, L, M = {"win"}, {"linux"}, {"mac"}
WL = {"win", "linux"}


def _r(pattern, keys, desc, fams=None):
    """Hilfsfunktion für Serien wie Strg+1 … Strg+9."""
    return [(pattern.format(k), desc.format(key_label(k)), fams) for k in keys]


OS_SHORTCUTS = {
    "win": [
        ("cmd+a", "Schnelleinstellungen"), ("cmd+b", "Infobereich fokussieren"),
        ("cmd+c", "Copilot"), ("cmd+d", "Desktop anzeigen"),
        ("cmd+e", "Explorer öffnen"), ("cmd+f", "Feedback-Hub"),
        ("cmd+g", "Xbox Game Bar"), ("cmd+h", "Diktat / Spracheingabe"),
        ("cmd+i", "Einstellungen"), ("cmd+k", "Verbinden (Streaming)"),
        ("cmd+l", "PC sperren"), ("cmd+m", "Alle Fenster minimieren"),
        ("cmd+n", "Benachrichtigungen / Kalender"), ("cmd+o", "Drehsperre"),
        ("cmd+p", "Projizieren"), ("cmd+q", "Suche"), ("cmd+r", "Ausführen"),
        ("cmd+s", "Suche"), ("cmd+t", "Taskleiste durchlaufen"),
        ("cmd+u", "Barrierefreiheit"), ("cmd+v", "Zwischenablageverlauf"),
        ("cmd+w", "Widgets"), ("cmd+x", "Schnelllink-Menü"), ("cmd+z", "Snap-Layouts"),
        ("cmd+shift+s", "Bildschirmausschnitt"),
        ("cmd+shift+m", "Minimierte Fenster wiederherstellen"),
        ("cmd+ctrl+d", "Neuer virtueller Desktop"),
        ("cmd+ctrl+f4", "Virtuellen Desktop schließen"),
        ("cmd+alt+r", "Bildschirmaufnahme (Game Bar)"),
        ("cmd+alt+d", "Datum/Uhrzeit anzeigen"),
        ("alt+f4", "Fenster / Programm schließen"),
    ] + _r("cmd+{}", "1234567890", "Programm {} der Taskleiste")
      + _r("cmd+shift+{}", "123456789", "Neue Instanz von Taskleisten-Programm {}")
      + _r("cmd+alt+{}", "123456789", "Sprungliste von Taskleisten-Programm {}"),

    "linux": [
        ("cmd+a", "App-Übersicht (GNOME)"), ("cmd+d", "Desktop anzeigen"),
        ("cmd+e", "Dateimanager (KDE/Cinnamon)"), ("cmd+h", "Fenster minimieren (GNOME)"),
        ("cmd+l", "Bildschirm sperren"), ("cmd+n", "Benachrichtigung fokussieren (GNOME)"),
        ("cmd+p", "Anzeigemodus wechseln"), ("cmd+s", "Schnelleinstellungen (GNOME)"),
        ("cmd+v", "Benachrichtigungen (GNOME) / Zwischenablage (KDE)"),
        ("ctrl+alt+t", "Terminal öffnen"), ("ctrl+alt+l", "Bildschirm sperren (KDE/XFCE)"),
        ("ctrl+alt+d", "Desktop anzeigen (XFCE)"),
        ("ctrl+alt+shift+r", "Bildschirmaufnahme (ältere GNOME-Versionen)"),
        ("alt+f1", "Anwendungsmenü"), ("alt+f2", "Befehl ausführen / KRunner"),
        ("alt+f3", "Fensteraktionen (KDE)"), ("alt+f4", "Fenster schließen"),
        ("alt+f5", "Fenster wiederherstellen"), ("alt+f7", "Fenster verschieben"),
        ("alt+f8", "Fenstergröße ändern"), ("alt+f10", "Maximieren umschalten"),
    ] + _r("ctrl+alt+{}", F_KEYS, "Wechsel auf Textkonsole ({}) – Vorsicht!")
      + _r("cmd+{}", "123456789", "Programm {} im Dock / in der Taskleiste")
      + _r("cmd+shift+{}", "123456789", "Fenster auf Arbeitsfläche {} verschieben")
      + _r("ctrl+{}", ["f1", "f2", "f3", "f4"], "Arbeitsfläche wechseln ({}, KDE)"),

    "mac": [
        ("cmd+q", "Programm beenden"), ("cmd+w", "Fenster schließen"),
        ("cmd+h", "Programm ausblenden"), ("cmd+alt+h", "Andere ausblenden"),
        ("cmd+m", "Fenster ins Dock"), ("cmd+alt+m", "Alle Fenster ins Dock"),
        ("cmd+n", "Neu"), ("cmd+o", "Öffnen"), ("cmd+s", "Sichern"),
        ("cmd+shift+s", "Sichern unter / Duplizieren"), ("cmd+p", "Drucken"),
        ("cmd+c", "Kopieren"), ("cmd+v", "Einsetzen"), ("cmd+x", "Ausschneiden"),
        ("cmd+z", "Widerrufen"), ("cmd+shift+z", "Wiederholen"),
        ("cmd+a", "Alles auswählen"), ("cmd+f", "Suchen"), ("cmd+g", "Weitersuchen"),
        ("cmd+shift+3", "Bildschirmfoto"), ("cmd+shift+4", "Bildschirmfoto (Auswahl)"),
        ("cmd+shift+5", "Bildschirmfoto / Aufnahme"),
        ("cmd+ctrl+q", "Bildschirm sperren"), ("cmd+shift+q", "Abmelden"),
        ("cmd+alt+d", "Dock ein-/ausblenden"), ("cmd+ctrl+f", "Vollbild"),
        ("cmd+shift+a", "Programme-Ordner (Finder)"),
        ("cmd+shift+d", "Schreibtisch-Ordner (Finder)"),
        ("cmd+shift+n", "Neuer Ordner (Finder)"),
    ] + _r("ctrl+{}", "123456789", "Zu Schreibtisch {} wechseln (falls aktiviert)"),
}

OS_SOURCE = {"win": "Windows", "linux": "Linux-Desktop", "mac": "macOS"}

# Windows + deutsche Tastatur: Strg+Alt wirkt wie AltGr
ALTGR_DE_WIN = [
    ("ctrl+alt+q", "= AltGr+Q → @"), ("ctrl+alt+e", "= AltGr+E → €"),
    ("ctrl+alt+m", "= AltGr+M → µ"), ("ctrl+alt+2", "= AltGr+2 → ²"),
    ("ctrl+alt+3", "= AltGr+3 → ³"), ("ctrl+alt+7", "= AltGr+7 → {"),
    ("ctrl+alt+8", "= AltGr+8 → ["), ("ctrl+alt+9", "= AltGr+9 → ]"),
    ("ctrl+alt+0", "= AltGr+0 → }"),
]

# macOS + deutsche Tastatur: Option erzeugt Sonderzeichen
OPTION_DE_MAC = [
    ("alt+l", "→ @"), ("alt+e", "→ €"), ("alt+5", "→ ["), ("alt+6", "→ ]"),
    ("alt+7", "→ |"), ("alt+8", "→ {"), ("alt+9", "→ }"), ("alt+n", "→ ~"),
    ("alt+shift+7", "→ \\"),
]

# ── Browser ──────────────────────────────────────────────────────────────────
CHROMIUM = [
    ("mod+t", "Neuer Tab"), ("mod+n", "Neues Fenster"),
    ("mod+shift+n", "Inkognito-/Privates Fenster"), ("mod+w", "Tab schließen"),
    ("mod+shift+w", "Fenster schließen"), ("mod+shift+t", "Geschlossenen Tab öffnen"),
    ("mod+l", "Adressleiste"), ("mod+d", "Lesezeichen setzen"),
    ("mod+shift+d", "Alle Tabs als Lesezeichen"), ("mod+h", "Verlauf"),
    ("mod+j", "Downloads"), ("mod+shift+b", "Lesezeichenleiste"),
    ("mod+shift+o", "Lesezeichen-Manager"), ("mod+p", "Drucken"),
    ("mod+s", "Seite speichern"), ("mod+u", "Quelltext"), ("mod+f", "Suchen"),
    ("mod+g", "Weitersuchen"), ("mod+r", "Neu laden"),
    ("mod+shift+r", "Neu laden ohne Cache"), ("mod+shift+i", "Entwicklertools"),
    ("mod+shift+j", "JavaScript-Konsole"), ("mod+shift+c", "Element untersuchen"),
    ("mod+o", "Datei öffnen"), ("mod+shift+m", "Profil wechseln"),
    ("mod+shift+a", "Tab-Suche"),
    ("mod+k", "Websuche", WL), ("mod+e", "Websuche", WL),
    ("alt+f", "Browsermenü", WL), ("alt+e", "Browsermenü", WL),
    ("alt+d", "Adressleiste", WL), ("alt+shift+i", "Feedback senden", WL),
    ("mod+shift+q", "Browser beenden", L), ("cmd+alt+i", "Entwicklertools", M),
    ("cmd+alt+j", "JavaScript-Konsole", M), ("cmd+alt+u", "Quelltext", M),
    ("cmd+y", "Verlauf", M), ("cmd+alt+b", "Lesezeichen-Manager", M),
    ("f1", "Hilfe"), ("f3", "Weitersuchen"), ("f5", "Neu laden"),
    ("f6", "Fokus Adressleiste"), ("f7", "Caret-Browsing"), ("f10", "Menü", WL),
    ("f11", "Vollbild"), ("f12", "Entwicklertools"),
] + _r("mod+{}", "12345678", "Zu Tab {} wechseln") + [("mod+9", "Zum letzten Tab")]

BRAVE_EXTRA = [("alt+shift+n", "Privates Fenster mit Tor", WL),
               ("cmd+alt+n", "Privates Fenster mit Tor", M)]
VIVALDI_EXTRA = [("f2", "Quick Commands"), ("mod+e", "Quick Commands"),
                 ("f4", "Seitenleiste ein/aus")]

FIREFOX = [
    ("mod+t", "Neuer Tab"), ("mod+n", "Neues Fenster"),
    ("mod+shift+p", "Privates Fenster"), ("mod+w", "Tab schließen"),
    ("mod+shift+w", "Fenster schließen"), ("mod+shift+t", "Geschlossenen Tab öffnen"),
    ("mod+l", "Adressleiste"), ("mod+k", "Websuche"), ("mod+e", "Websuche", WL),
    ("mod+d", "Lesezeichen setzen"), ("mod+shift+d", "Alle Tabs als Lesezeichen"),
    ("mod+b", "Lesezeichen-Sidebar"), ("mod+shift+b", "Lesezeichen-Symbolleiste"),
    ("mod+shift+o", "Bibliothek (Lesezeichen)"), ("mod+h", "Chronik-Sidebar"),
    ("mod+shift+h", "Bibliothek (Chronik)"), ("mod+j", "Downloads"),
    ("mod+shift+y", "Downloads", L), ("mod+p", "Drucken"), ("mod+s", "Seite speichern"),
    ("mod+u", "Quelltext"), ("mod+f", "Suchen"), ("mod+g", "Weitersuchen"),
    ("mod+r", "Neu laden"), ("mod+shift+r", "Neu laden ohne Cache"),
    ("mod+shift+i", "Werkzeuge für Web-Entwickler"), ("mod+shift+k", "Webkonsole"),
    ("mod+shift+c", "Element untersuchen"), ("mod+shift+e", "Netzwerkanalyse"),
    ("mod+shift+m", "Bildschirmgrößen testen"), ("mod+i", "Seiteninformationen"),
    ("mod+shift+a", "Add-ons und Themes"), ("mod+o", "Datei öffnen"),
    ("mod+alt+r", "Leseansicht", M), ("f9", "Leseansicht", WL),
    ("mod+q", "Firefox beenden", L), ("mod+shift+q", "Firefox beenden", W),
    ("f1", "Hilfe"), ("f3", "Weitersuchen"), ("f5", "Neu laden"),
    ("f6", "Fokus Adressleiste"), ("f7", "Caret-Browsing"), ("f10", "Menüleiste", WL),
    ("f11", "Vollbild"), ("f12", "Entwicklerwerkzeuge"),
] + _r("mod+{}", "12345678", "Zu Tab {} wechseln") + [("mod+9", "Zum letzten Tab")]

SAFARI = [
    ("cmd+t", "Neuer Tab"), ("cmd+n", "Neues Fenster"),
    ("cmd+shift+n", "Privates Fenster"), ("cmd+w", "Tab schließen"),
    ("cmd+shift+w", "Fenster schließen"), ("cmd+shift+t", "Geschlossenen Tab öffnen"),
    ("cmd+l", "Adressfeld"), ("cmd+d", "Lesezeichen hinzufügen"),
    ("cmd+shift+d", "Zur Leseliste"), ("cmd+alt+b", "Lesezeichen bearbeiten"),
    ("cmd+ctrl+1", "Lesezeichen-Seitenleiste"), ("cmd+shift+l", "Seitenleiste"),
    ("cmd+alt+l", "Downloads"), ("cmd+y", "Verlauf"), ("cmd+shift+r", "Reader"),
    ("cmd+alt+i", "Webinformationen"), ("cmd+alt+c", "JavaScript-Konsole"),
    ("cmd+alt+e", "Cache leeren"), ("cmd+alt+u", "Quelltext"), ("cmd+r", "Neu laden"),
    ("cmd+p", "Drucken"), ("cmd+s", "Sichern"), ("cmd+f", "Suchen"),
    ("cmd+g", "Weitersuchen"),
] + _r("cmd+{}", "123456789", "Tab / Favorit {}")

BROWSER_SHORTCUTS = {
    "chrome": CHROMIUM, "chromium": CHROMIUM, "edge": CHROMIUM,
    "brave": CHROMIUM + BRAVE_EXTRA, "vivaldi": CHROMIUM + VIVALDI_EXTRA,
    "firefox": FIREFOX, "safari": SAFARI,
}

# ── Textverarbeitungen ───────────────────────────────────────────────────────
_EDIT_BASICS = [("mod+a", "Alles markieren"), ("mod+c", "Kopieren"),
                ("mod+v", "Einfügen"), ("mod+x", "Ausschneiden"),
                ("mod+z", "Rückgängig"), ("mod+y", "Wiederholen")]

GDOCS = _EDIT_BASICS + [
    ("mod+b", "Fett"), ("mod+i", "Kursiv"), ("mod+u", "Unterstrichen"),
    ("mod+k", "Link einfügen"), ("mod+f", "Suchen"), ("mod+h", "Suchen & Ersetzen"),
    ("mod+s", "Speichern (ohne Funktion)"), ("mod+p", "Drucken"), ("mod+o", "Datei öffnen"),
    ("mod+shift+v", "Ohne Formatierung einfügen"), ("mod+alt+c", "Format kopieren"),
    ("mod+alt+v", "Format einfügen"), ("mod+shift+c", "Wortanzahl"),
    ("mod+shift+l", "Linksbündig"), ("mod+shift+e", "Zentriert"),
    ("mod+shift+r", "Rechtsbündig"), ("mod+shift+j", "Blocksatz"),
    ("mod+shift+7", "Nummerierte Liste"), ("mod+shift+8", "Aufzählung"),
    ("mod+shift+9", "Checkliste"), ("mod+alt+m", "Kommentar einfügen"),
    ("mod+alt+shift+a", "Kommentarverlauf"), ("mod+alt+shift+h", "Versionsverlauf"),
    ("mod+alt+x", "Rechtschreibprüfung"), ("mod+shift+s", "Spracheingabe"),
    ("mod+shift+f", "Kompaktmodus"), ("alt+shift+5", "Durchgestrichen", WL),
    ("cmd+shift+x", "Durchgestrichen", M), ("ctrl+shift+x", "Kontextmenü", WL),
] + _r("mod+alt+{}", "0123456", "Absatzformat {} (0 = Normal, 1–6 = Überschrift)") \
  + _r("alt+{}", "fevioth", "Menü öffnen (Chrome)", WL) \
  + _r("alt+shift+{}", "fevioth", "Menü öffnen (andere Browser)", WL) \
  + _r("ctrl+alt+{}", "fevioth", "Menü öffnen", M)

WORD = _EDIT_BASICS + [
    ("mod+b", "Fett (engl. Word) / Blocksatz (dt. Word)"), ("mod+d", "Schriftart-Dialog"),
    ("mod+e", "Zentrieren"), ("mod+f", "Suchen / Navigationsbereich"),
    ("mod+g", "Gehe zu"), ("mod+h", "Ersetzen"), ("mod+i", "Kursiv (engl. Word)"),
    ("mod+j", "Blocksatz (engl. Word)"), ("mod+k", "Hyperlink einfügen"),
    ("mod+l", "Linksbündig"), ("mod+m", "Einzug vergrößern"),
    ("mod+shift+m", "Einzug verkleinern"), ("mod+n", "Neues Dokument"),
    ("mod+o", "Öffnen"), ("mod+p", "Drucken"), ("mod+q", "Absatzformatierung entfernen"),
    ("mod+r", "Rechtsbündig"), ("mod+s", "Speichern"), ("mod+t", "Hängender Einzug"),
    ("mod+u", "Unterstrichen"), ("mod+w", "Dokument schließen"),
    ("mod+1", "Einfacher Zeilenabstand"), ("mod+2", "Doppelter Zeilenabstand"),
    ("mod+5", "1,5-facher Zeilenabstand"), ("mod+0", "Abstand vor Absatz"),
    ("mod+shift+f", "Fett (dt. Word)"), ("mod+shift+k", "Kursiv (dt. Word)"),
    ("mod+shift+u", "Unterstrichen (dt. Word)"), ("mod+shift+d", "Doppelt unterstreichen"),
    ("mod+shift+a", "Großbuchstaben"), ("mod+shift+g", "Großbuchstaben / Wortanzahl"),
    ("mod+shift+c", "Format kopieren"), ("mod+shift+v", "Format übertragen"),
    ("mod+shift+n", "Formatvorlage Standard"), ("mod+shift+l", "Formatvorlage Liste"),
    ("mod+shift+s", "Formatvorlage anwenden"), ("mod+shift+e", "Änderungen nachverfolgen"),
    ("mod+shift+h", "Verborgener Text"), ("mod+shift+w", "Wörter unterstreichen"),
    ("mod+shift+q", "Symbol-Schriftart"), ("mod+shift+p", "Schriftgrad wählen"),
    ("mod+alt+1", "Überschrift 1"), ("mod+alt+2", "Überschrift 2"),
    ("mod+alt+3", "Überschrift 3"), ("mod+alt+c", "©-Zeichen"),
    ("mod+alt+r", "®-Zeichen"), ("mod+alt+t", "™-Zeichen"),
    ("mod+alt+m", "Kommentar einfügen"), ("mod+alt+f", "Fußnote einfügen"),
    ("mod+alt+d", "Endnote einfügen"), ("mod+alt+n", "Entwurfsansicht"),
    ("mod+alt+o", "Gliederungsansicht"), ("mod+alt+p", "Seitenlayout-Ansicht"),
    ("mod+alt+s", "Fenster teilen"), ("mod+alt+k", "AutoFormat"),
    ("mod+alt+l", "ListNum-Feld"), ("mod+alt+i", "Druckvorschau"),
    ("mod+alt+v", "Inhalte einfügen"),
    ("alt+shift+d", "Datum einfügen"), ("alt+shift+t", "Uhrzeit einfügen"),
    ("alt+shift+p", "Seitenzahl einfügen"), ("alt+shift+o", "Verzeichniseintrag"),
    ("alt+shift+x", "Indexeintrag"), ("alt+shift+i", "Zitat markieren"),
] + _r("alt+shift+{}", "123456789", "Gliederung bis Ebene {}") + [
    # F-Tasten (Windows-Belegung)
    ("f1", "Hilfe", W), ("f2", "Text verschieben", W), ("f3", "AutoText", W),
    ("f4", "Letzte Aktion wiederholen", W), ("f5", "Gehe zu", W),
    ("f6", "Nächster Bereich", W), ("f7", "Rechtschreibung", W),
    ("f8", "Markierungsmodus", W), ("f9", "Felder aktualisieren", W),
    ("f10", "Menüband-Tasten", W), ("f11", "Nächstes Feld", W),
    ("f12", "Speichern unter", W),
    ("shift+f1", "Formatierung anzeigen", W), ("shift+f2", "Text kopieren", W),
    ("shift+f3", "Groß-/Kleinschreibung", W), ("shift+f4", "Suche wiederholen", W),
    ("shift+f5", "Letzte Bearbeitungsstelle", W), ("shift+f6", "Vorheriger Bereich", W),
    ("shift+f7", "Thesaurus", W), ("shift+f8", "Markierung verkleinern", W),
    ("shift+f9", "Feldfunktion umschalten", W), ("shift+f10", "Kontextmenü", W),
    ("shift+f11", "Vorheriges Feld", W), ("shift+f12", "Speichern", W),
    ("ctrl+f1", "Menüband ein/aus", W), ("ctrl+f2", "Druckvorschau", W),
    ("ctrl+f3", "In Sammlung ausschneiden", W), ("ctrl+f4", "Fenster schließen", W),
    ("ctrl+f5", "Fenster wiederherstellen", W), ("ctrl+f6", "Nächstes Fenster", W),
    ("ctrl+f9", "Leeres Feld einfügen", W), ("ctrl+f10", "Maximieren", W),
    ("ctrl+f11", "Feld sperren", W), ("ctrl+f12", "Öffnen", W),
    ("ctrl+shift+f3", "Sammlung einfügen", W), ("ctrl+shift+f5", "Textmarke", W),
    ("ctrl+shift+f6", "Vorheriges Fenster", W),
    ("ctrl+shift+f7", "Verknüpfungen aktualisieren", W),
    ("ctrl+shift+f8", "Spaltenmarkierung", W), ("ctrl+shift+f9", "Feldverknüpfung lösen", W),
    ("ctrl+shift+f11", "Feld entsperren", W), ("ctrl+shift+f12", "Drucken", W),
    ("alt+f1", "Nächstes Feld", W), ("alt+f3", "Baustein erstellen", W),
    ("alt+f5", "Fenster wiederherstellen", W), ("alt+f7", "Nächster Fehler", W),
    ("alt+f8", "Makros", W), ("alt+f9", "Alle Feldfunktionen", W),
    ("alt+f10", "Auswahlbereich", W), ("alt+f11", "VBA-Editor", W),
    ("alt+shift+f1", "Vorheriges Feld", W), ("alt+shift+f2", "Speichern", W),
    ("alt+shift+f7", "Übersetzen", W), ("alt+shift+f9", "GotoButton/MacroButton", W),
    ("alt+shift+f10", "Smarttag-Menü", W),
]

WORD_WEB = _EDIT_BASICS + [
    ("mod+b", "Fett"), ("mod+i", "Kursiv"), ("mod+u", "Unterstrichen"),
    ("mod+e", "Zentrieren"), ("mod+l", "Linksbündig"), ("mod+r", "Rechtsbündig"),
    ("mod+j", "Blocksatz"), ("mod+k", "Link einfügen"), ("mod+f", "Suchen"),
    ("mod+h", "Ersetzen"), ("mod+s", "Speichern"), ("mod+p", "Drucken"),
    ("mod+m", "Einzug vergrößern"), ("mod+shift+m", "Einzug verkleinern"),
    ("mod+alt+1", "Überschrift 1"), ("mod+alt+2", "Überschrift 2"),
    ("mod+alt+3", "Überschrift 3"), ("mod+alt+m", "Kommentar einfügen"),
    ("mod+alt+f", "Fußnote einfügen"), ("mod+shift+c", "Format kopieren"),
    ("mod+shift+v", "Format einfügen"), ("mod+shift+n", "Formatvorlage Standard"),
    ("mod+shift+l", "Aufzählung"), ("mod+shift+e", "Änderungen nachverfolgen"),
]

LIBREOFFICE = _EDIT_BASICS + [
    ("mod+b", "Fett"), ("mod+d", "Doppelt unterstreichen"), ("mod+e", "Zentrieren"),
    ("mod+f", "Suchleiste"), ("mod+h", "Suchen & Ersetzen"), ("mod+i", "Kursiv"),
    ("mod+j", "Blocksatz"), ("mod+k", "Hyperlink"), ("mod+l", "Linksbündig"),
    ("mod+m", "Direkte Formatierung entfernen"), ("mod+n", "Neues Dokument"),
    ("mod+o", "Öffnen"), ("mod+p", "Drucken"), ("mod+q", "LibreOffice beenden"),
    ("mod+r", "Rechtsbündig"), ("mod+s", "Speichern"), ("mod+u", "Unterstrichen"),
    ("mod+w", "Fenster schließen"), ("mod+0", "Absatzvorlage Textkörper"),
] + _r("mod+{}", "12345", "Überschrift {}") + [
    ("mod+shift+p", "Hochgestellt"), ("mod+shift+b", "Tiefgestellt"),
    ("mod+shift+c", "Änderungen aufzeichnen"), ("mod+shift+j", "Vollbild"),
    ("mod+shift+n", "Vorlagen verwalten"), ("mod+shift+o", "Druckvorschau"),
    ("mod+shift+r", "Lineal ein/aus"), ("mod+shift+s", "Speichern unter"),
    ("mod+shift+v", "Inhalte einfügen"), ("mod+alt+shift+v", "Unformatiert einfügen"),
    ("mod+alt+c", "Kommentar einfügen"),
    ("f1", "Hilfe"), ("f2", "Formel einfügen"), ("f3", "AutoText"),
    ("f5", "Navigator"), ("f7", "Rechtschreibung"), ("f8", "Erweiterungsmodus"),
    ("f9", "Felder aktualisieren"), ("f10", "Menüleiste", WL),
    ("f11", "Formatvorlagen"), ("f12", "Nummerierung ein"),
    ("shift+f3", "Groß-/Kleinschreibung"), ("shift+f8", "Blockmarkierung"),
    ("shift+f10", "Kontextmenü"), ("shift+f11", "Vorlage aus Auswahl"),
    ("shift+f12", "Aufzählung ein"), ("mod+shift+f12", "Nummerierung aus"),
    ("mod+f2", "Feldbefehle"), ("mod+f3", "AutoText bearbeiten"),
    ("mod+f7", "Thesaurus"), ("mod+f8", "Feldhinterlegungen"),
    ("mod+f9", "Feldnamen anzeigen"), ("mod+f10", "Formatierungszeichen"),
    ("mod+f12", "Tabelle einfügen"), ("mod+shift+f10", "Fenster andocken"),
    ("alt+f12", "Optionen"),
]

COLLABORA = _EDIT_BASICS + [
    ("mod+b", "Fett"), ("mod+i", "Kursiv"), ("mod+u", "Unterstrichen"),
    ("mod+d", "Doppelt unterstreichen"), ("mod+e", "Zentrieren"),
    ("mod+l", "Linksbündig"), ("mod+r", "Rechtsbündig"), ("mod+j", "Blocksatz"),
    ("mod+f", "Suchen"), ("mod+h", "Suchen & Ersetzen"), ("mod+k", "Hyperlink"),
    ("mod+p", "Drucken"), ("mod+s", "Speichern"), ("mod+m", "Formatierung entfernen"),
    ("mod+0", "Textkörper"),
] + _r("mod+{}", "12345", "Überschrift {}") + [
    ("mod+shift+p", "Hochgestellt"), ("mod+shift+b", "Tiefgestellt"),
    ("mod+shift+v", "Inhalte einfügen"), ("mod+alt+shift+v", "Unformatiert einfügen"),
    ("mod+alt+c", "Kommentar einfügen"), ("mod+shift+c", "Änderungen aufzeichnen"),
]

# key: (Anzeigename, webbasiert?, Einträge)
PROCESSORS = {
    "gdocs":       ("Google Docs", True, GDOCS),
    "word":        ("MS Word (Desktop)", False, WORD),
    "wordweb":     ("MS Word (Web / Microsoft 365)", True, WORD_WEB),
    "libreoffice": ("LibreOffice Writer", False, LIBREOFFICE),
    "collabora":   ("Collabora Online", True, COLLABORA),
}
PROCESSOR_CHOICES = [(k, v[0]) for k, v in PROCESSORS.items()]
