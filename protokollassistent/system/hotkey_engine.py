"""Globale Hotkeys (systemweit, auch wenn ein anderes Programm im Vordergrund ist)
und automatisches Einfügen per Strg+V / Cmd+V."""
from __future__ import annotations

import threading
import time

from PySide6 import QtCore
from PySide6.QtCore import Signal

from ..core.combos import parse_combo
from ..core.constants import F_KEYS, IS_MAC, IS_WIN

try:
    from pynput import keyboard
    PYNPUT_ERROR = None
except Exception as exc:  # pragma: no cover – z. B. Linux ohne X-Server
    keyboard = None
    PYNPUT_ERROR = f"{type(exc).__name__}: {exc}"


# macOS: Hardware-Tastencodes (ANSI-Anordnung) → Taste
MAC_KEYCODES = {0: "a", 1: "s", 2: "d", 3: "f", 4: "h", 5: "g", 6: "z", 7: "x", 8: "c",
                9: "v", 11: "b", 12: "q", 13: "w", 14: "e", 15: "r", 16: "y", 17: "t",
                18: "1", 19: "2", 20: "3", 21: "4", 22: "6", 23: "5", 25: "9", 26: "7",
                28: "8", 29: "0", 31: "o", 32: "u", 34: "i", 35: "p", 37: "l", 38: "j",
                40: "k", 45: "n", 46: "m"}

# Linux/X11 liefert mit Umschalt das umgeschaltete Zeichen – zurück auf die Ziffer
SHIFT_DIGITS = {
    "de": {"!": "1", '"': "2", "§": "3", "$": "4", "%": "5", "&": "6",
           "/": "7", "(": "8", ")": "9", "=": "0"},
    "us": {"!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6",
           "&": "7", "*": "8", "(": "9", ")": "0"},
}

WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP = 0x100, 0x101, 0x104, 0x105
LLKHF_INJECTED = 0x10


def available() -> bool:
    return keyboard is not None


def _win_vk_name(vk) -> str | None:
    if vk is None:
        return None
    if 0x30 <= vk <= 0x39 or 0x41 <= vk <= 0x5A:
        return chr(vk).lower()
    if 0x70 <= vk <= 0x7B:
        return f"f{vk - 0x6F}"
    return None


def _mod_name(key) -> str | None:
    K = keyboard.Key
    if key in (K.ctrl, K.ctrl_l, K.ctrl_r):
        return "ctrl"
    if key in (K.shift, K.shift_l, K.shift_r):
        return "shift"
    if key in (K.cmd, K.cmd_l, K.cmd_r):
        return "cmd"
    if key in (K.alt, K.alt_l, K.alt_r):
        return "alt"
    if IS_MAC and key == K.alt_gr:
        return "alt"
    return None          # AltGr unter Linux/Windows zählt bewusst nicht als Alt


class HotkeyEngine(QtCore.QObject):
    """Lauscht systemweit auf Tastendrücke und meldet erkannte Hotkeys.

    Das Signal ``triggered`` liefert die ID des Textblocks. Es wird aus dem
    pynput-Thread gesendet; Qt stellt es automatisch im GUI-Thread zu.
    """
    triggered = Signal(str)

    def __init__(self):
        super().__init__()
        self._map: dict = {}
        self._mods: set[str] = set()
        self._fired: set[str] = set()
        self._listener = None
        self._busy = False
        self.injecting = False
        self.layout = "de"
        self.suppress = True

    # ── Steuerung ──
    def set_hotkeys(self, mapping: dict[str, str]) -> None:
        """mapping: {'ctrl+shift+1': block_id, ...}"""
        new = {}
        for combo, bid in mapping.items():
            p = parse_combo(combo)
            if p:
                new[p] = bid
        self._map = new

    @property
    def count(self) -> int:
        return len(self._map)

    @property
    def running(self) -> bool:
        return self._listener is not None

    def start(self) -> None:
        if keyboard is None:
            raise RuntimeError(PYNPUT_ERROR or "pynput nicht verfügbar")
        self.stop()
        self._mods.clear()
        self._fired.clear()
        kwargs = {}
        if IS_WIN and self.suppress:
            kwargs["win32_event_filter"] = self._win32_filter
        self._listener = keyboard.Listener(on_press=self._on_press,
                                           on_release=self._on_release, **kwargs)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    # ── Tastenerkennung ──
    def _resolve(self, key) -> str | None:
        if isinstance(key, keyboard.Key):
            return key.name if key.name in F_KEYS else None
        vk = getattr(key, "vk", None)
        ch = getattr(key, "char", None)
        if IS_WIN and vk is not None:
            return _win_vk_name(vk)
        if IS_MAC and vk is not None and vk in MAC_KEYCODES:
            n = MAC_KEYCODES[vk]
            if self.layout == "de" and n in ("y", "z"):
                n = "z" if n == "y" else "y"
            return n
        if ch:
            c = ch.lower()
            c = SHIFT_DIGITS.get(self.layout, {}).get(c, c)
            if len(c) == 1 and ("a" <= c <= "z" or "0" <= c <= "9"):
                return c
        if vk is not None and not IS_MAC:        # X11-Keysym
            if 0x30 <= vk <= 0x39 or 0x61 <= vk <= 0x7A:
                return chr(vk)
            if 0x41 <= vk <= 0x5A:
                return chr(vk).lower()
        return None

    def _on_press(self, key):
        if key is None:
            return
        m = _mod_name(key)
        if m:
            self._mods.add(m)
            return
        if self.injecting or (IS_WIN and self.suppress):
            return                                  # Windows: siehe _win32_filter
        name = self._resolve(key)
        if not name:
            return
        bid = self._map.get((frozenset(self._mods), name))
        if bid and name not in self._fired:
            self._fired.add(name)
            self.triggered.emit(bid)

    def _on_release(self, key):
        if key is None:
            return
        m = _mod_name(key)
        if m:
            self._mods.discard(m)
        elif not (IS_WIN and self.suppress):
            self._fired.clear()

    def _win32_filter(self, msg, data):
        """Windows: Hotkey erkennen und vor dem Zielprogramm verstecken."""
        if data.flags & LLKHF_INJECTED:
            return True
        name = _win_vk_name(data.vkCode)
        if name is None:
            return True
        if msg in (WM_KEYDOWN, WM_SYSKEYDOWN):
            bid = self._map.get((frozenset(self._mods), name))
            if bid:
                if name not in self._fired:
                    self._fired.add(name)
                    self.triggered.emit(bid)
                self._listener.suppress_event()
        elif msg in (WM_KEYUP, WM_SYSKEYUP) and name in self._fired:
            self._fired.discard(name)
            self._listener.suppress_event()
        return True

    # ── Einfügen ──
    def paste(self, enter_after: int = 0, mask_menu: bool = False) -> None:
        """Wartet, bis die Hotkey-Tasten losgelassen sind, und drückt dann Strg/Cmd+V."""
        if self._busy or keyboard is None:
            return
        self._busy = True

        def work():
            ctl = keyboard.Controller()
            K = keyboard.Key
            try:
                if mask_menu and IS_WIN:
                    # Neutrale Taste, damit das Loslassen von Alt/Win kein Menü öffnet
                    self.injecting = True
                    mask = keyboard.KeyCode.from_vk(0xE8)
                    ctl.press(mask)
                    ctl.release(mask)
                    self.injecting = False
                t0 = time.monotonic()
                while self._mods and time.monotonic() - t0 < 1.5:
                    time.sleep(0.02)
                self.injecting = True
                if self._mods:                        # Notfall: Tasten hängen
                    for k in (K.ctrl, K.alt, K.shift, K.cmd):
                        try:
                            ctl.release(k)
                        except Exception:
                            pass
                    self._mods.clear()
                time.sleep(0.05)
                mod = K.cmd if IS_MAC else K.ctrl
                ctl.press(mod)
                ctl.press("v")
                ctl.release("v")
                ctl.release(mod)
                if enter_after:
                    time.sleep(0.15)
                    for _ in range(enter_after):
                        ctl.press(K.enter)
                        ctl.release(K.enter)
                        time.sleep(0.05)
            finally:
                time.sleep(0.05)
                self.injecting = False
                self._busy = False

        threading.Thread(target=work, daemon=True).start()
