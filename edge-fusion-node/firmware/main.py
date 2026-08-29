"""Control loop for the edge-fusion node.

This file is intentionally designed to run under both MicroPython and CPython
by using the local mock abstractions when device modules are unavailable.
"""

from __future__ import annotations

import time

from .config import CRITICAL_THRESHOLD, MOCK_HARDWARE, WARNING_THRESHOLD
from .fusion import calculate_fusion_score, score_to_level
from .indicators import IndicatorController
from .lora_link import LoRaLink
from .sensors import SensorManager


class FusionNode:
    def __init__(self):
        self.sensors = SensorManager()
        self.indicators = IndicatorController()
        self.lora = LoRaLink()
        self.node_id = "001"

    def read_cycle(self):
        readings = self.sensors.read()
        score = calculate_fusion_score(
            readings.temperature_c,
            readings.gas_raw,
            readings.motion,
        )
        level = score_to_level(score)
        self.indicators.set_level(level)
        self.indicators.buzz(level in {"WARNING", "CRITICAL"})
        payload = f"ID:{self.node_id}|T:{readings.temperature_c}|G:{readings.gas_raw}|SCORE:{score}|LVL:{level}"
        self.lora.send(payload)
        return {
            "temperature_c": readings.temperature_c,
            "humidity_pct": readings.humidity_pct,
            "gas_raw": readings.gas_raw,
            "motion": readings.motion,
            "score": score,
            "level": level,
            "payload": payload,
        }

    def run(self, interval_seconds: float = 2.0):
        self.lora.begin()
        while True:
            self.read_cycle()
            time.sleep(interval_seconds)


if __name__ == "__main__":
    node = FusionNode()
    node.run()
