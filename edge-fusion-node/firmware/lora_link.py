"""LoRa communication wrapper.

This module intentionally exposes a narrow interface so a real SX1276 driver can
be dropped in later without changing the rest of the firmware logic.
"""

from __future__ import annotations

import json
import time

from .config import LORA_BAND, LORA_BW, LORA_CS_PIN, LORA_IRQ_PIN, LORA_RESET_PIN, LORA_SF


class LoRaLink:
    """Simple gateway wrapper around a physical LoRa driver implementation."""

    def __init__(self, driver=None):
        self.driver = driver or MockLoRaDriver()

    def begin(self):
        return self.driver.begin()

    def send(self, payload: str):
        return self.driver.send(payload)

    def recv(self):
        return self.driver.recv()


class MockLoRaDriver:
    """A tiny in-memory stub used for testing and local simulation."""

    def __init__(self):
        self.buffer = []

    def begin(self):
        return True

    def send(self, payload: str):
        self.buffer.append(payload)
        return True

    def recv(self):
        if not self.buffer:
            return None
        result = self.buffer.pop(0)
        return result
