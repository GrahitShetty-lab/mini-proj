"""Sensor read wrappers and mock implementations for local testing."""

from __future__ import annotations

import random
import time

from .config import MOCK_HARDWARE, PIN_DHT22, PIN_MQ2, PIN_PIR


class MockDHT22:
    def __init__(self, pin: int):
        self.pin = pin

    def temperature(self):
        return 22.0

    def humidity(self):
        return 52.0


class MockMQ2:
    def __init__(self, pin: int):
        self.pin = pin

    def read(self):
        return 400


class MockPIR:
    def __init__(self, pin: int):
        self.pin = pin

    @property
    def value(self):
        return 0


class SensorReadings:
    def __init__(self, temperature_c: float, humidity_pct: float, gas_raw: int, motion: bool):
        self.temperature_c = temperature_c
        self.humidity_pct = humidity_pct
        self.gas_raw = gas_raw
        self.motion = motion


class SensorManager:
    """Thin abstraction that works on device hardware or in CPython mock mode."""

    def __init__(self):
        self.use_mock = MOCK_HARDWARE
        self.dht = MockDHT22(PIN_DHT22) if self.use_mock else _build_real_dht()
        self.gas = MockMQ2(PIN_MQ2) if self.use_mock else _build_real_gas()
        self.pir = MockPIR(PIN_PIR) if self.use_mock else _build_real_pir()

    def read(self):
        if self.use_mock:
            return SensorReadings(
                temperature_c = 22.0,
                humidity_pct = 50.0,
                gas_raw = 400,
                motion = False,
            )
        return SensorReadings(
            temperature_c=float(self.dht.temperature()),
            humidity_pct=float(self.dht.humidity()),
            gas_raw=int(self.gas.read()),
            motion=bool(self.pir.value),
        )


def _build_real_dht():
    try:
        import dht

        return dht.DHT22
    except Exception:
        return MockDHT22(PIN_DHT22)


def _build_real_gas():
    try:
        from machine import ADC

        return ADC(PIN_MQ2)
    except Exception:
        return MockMQ2(PIN_MQ2)


def _build_real_pir():
    try:
        from machine import Pin

        return Pin(PIN_PIR, Pin.IN)
    except Exception:
        return MockPIR(PIN_PIR)
