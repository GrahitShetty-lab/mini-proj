"""LED and buzzer interfaces for local and hardware outputs."""

from __future__ import annotations

try:
    import machine
except Exception:  # pragma: no cover - CPython fallback only.
    machine = None

from .config import PIN_BUZZER, PIN_RGB_BLUE, PIN_RGB_GREEN, PIN_RGB_RED, RGB_CRITICAL, RGB_NORMAL, RGB_WARNING


class IndicatorController:
    def __init__(self):
        self._has_hw = machine is not None
        if self._has_hw:
            self.red = machine.Pin(PIN_RGB_RED, machine.Pin.OUT)
            self.green = machine.Pin(PIN_RGB_GREEN, machine.Pin.OUT)
            self.blue = machine.Pin(PIN_RGB_BLUE, machine.Pin.OUT)
            self.buzzer = machine.Pin(PIN_BUZZER, machine.Pin.OUT)
        else:
            self.red = None
            self.green = None
            self.blue = None
            self.buzzer = None

    def set_level(self, level: str):
        if not self._has_hw:
            return
        rgb = {
            "NORMAL": RGB_NORMAL,
            "WARNING": RGB_WARNING,
            "CRITICAL": RGB_CRITICAL,
        }.get(level, RGB_NORMAL)
        self.red.value(1 if rgb[0] > 0 else 0)
        self.green.value(1 if rgb[1] > 0 else 0)
        self.blue.value(1 if rgb[2] > 0 else 0)

    def buzz(self, enabled: bool):
        if self.buzzer is not None:
            self.buzzer.value(1 if enabled else 0)
