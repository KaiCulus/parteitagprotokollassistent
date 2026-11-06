# Protokollassistent

Formatierte Textblöcke per globalem Hotkey direkt in die offene Textverarbeitung
schreiben – mit automatisch eingesetzter Systemzeit (`{{Systime}}`).

## Installation

```
pip install -r requirements.txt
```

* **Windows:**  `py -m pip install -r requirements.txt`
* **macOS:** danach unter *Systemeinstellungen → Datenschutz & Sicherheit*
  „Bedienungshilfen“ und „Eingabeüberwachung“ für Terminal/Python erlauben.
* **Linux:** Globale Hotkeys funktionieren zuverlässig nur in einer X11-Sitzung
  (nicht Wayland). Im Zweifel einfach "sudo pacman -S xfce4", ausloggen und eine neue Desktopsession mit xfce starten. Debian ggf. zusätzlich: `sudo apt install libxcb-cursor0`

## Start

```
python start.py
```
(oder `python -m protokollassistent`)

## Bedienung

* **Neuer Hotkey** – Tastenkombination wählen, Text eingeben und formatieren
  (Fett, Kursiv, Farben, Größe …). **Systemzeit einfügen** setzt `{{Systime}}`
  ein; beim Auslösen wird daraus die aktuelle Uhrzeit.
* **Ändern / Löschen** – in jeder Tabellenzeile (Doppelklick = Ändern).
* **Betriebssystem / Browser / Textverarbeitung festlegen** – danach richtet sich
  die Warnung vor bereits belegten Tastenkürzeln. Hier auch das Zeitformat.
* Ist ein Hotkey schon belegt (durch einen anderen Textblock, das System oder die
  Textverarbeitung), erscheint eine Warnung. Beim Überschreiben verliert ein
  anderer Textblock seinen Hotkey.
* Solange der Protokollassistent selbst im Vordergrund ist, wird nichts eingefügt.

## Speicherung

Alles wird nach jeder Änderung automatisch in `textbloecke.xml` neben `start.py`
gespeichert (falls der Ordner schreibgeschützt ist: im Benutzerprofil) und beim
nächsten Start wieder geladen. Dateien der Vorgängerversion (`protokollhelfer`)
werden ebenfalls gelesen; `{SYSTEMTIME}` wird dabei zu `{{Systime}}`.

## Aufbau

```
start.py                         Startskript
protokollassistent/
├── app.py                       QApplication + Hauptfenster
├── core/                        Logik ohne Qt
│   ├── constants.py             Plattform, Auswahllisten, Tastennamen
│   ├── combos.py                Hotkey-Notation (parsen, anzeigen)
│   ├── shortcut_db.py           Datenbank bekannter Tastenkürzel
│   ├── conflicts.py             Konfliktprüfung, freie Vorschläge
│   ├── model.py                 Settings, Run, Block
│   ├── placeholders.py          {{Systime}}, {{Datum}}, {{Wochentag}}
│   ├── render.py                Textblock → HTML / Nur-Text
│   └── storage.py               XML speichern / laden
├── system/
│   ├── hotkey_engine.py         globale Hotkeys (pynput) + Einfügen
│   └── clipboard.py             Zwischenablage
└── ui/
    ├── theme.py                 Farben, Stylesheets
    ├── main_window.py           Hauptfenster
    ├── block_table.py           Tabelle mit Ändern/Löschen
    ├── block_dialog.py          Dialog Neuer Hotkey / Ändern
    ├── hotkey_input.py          Hotkey-Auswahl mit Live-Warnung
    ├── format_toolbar.py        Formatierungsleiste
    ├── rich_text.py             Editor ↔ Datenmodell
    ├── settings_dialog.py       Umgebung & Zeitformat
    └── overview_dialog.py       Übersicht belegter Kürzel
```
