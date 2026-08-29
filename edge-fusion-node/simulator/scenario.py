from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Packet:
    node_id: str
    temperature_c: float
    gas_raw: int
    motion: bool
    score: float
    level: str

    def render(self) -> str:
        return f"ID:{self.node_id}|T:{self.temperature_c}|G:{self.gas_raw}|SCORE:{self.score}|LVL:{self.level}"


def score_for(temp: float, gas: int, motion: bool) -> tuple[float, str]:
    temp_component = 0.0
    if temp >= 45.0:
        temp_component = 100.0
    elif temp > 30.0:
        temp_component = ((temp - 30.0) / 15.0) * 100.0

    gas_component = 0.0
    if gas >= 1500:
        gas_component = 100.0
    elif gas > 500:
        gas_component = ((gas - 500.0) / 1000.0) * 100.0

    score = temp_component + gas_component + (20.0 if motion else 0.0)
    if score > 100.0:
        score = 100.0
    if score >= 75.0:
        level = "CRITICAL"
    elif score >= 40.0:
        level = "WARNING"
    else:
        level = "NORMAL"
    return round(score, 2), level


def scenario_fire_drill() -> list[Packet]:
    packets: list[Packet] = []
    for phase in [
        (22.0, 420, False),
        (31.0, 600, False),
        (33.0, 820, False),
        (38.0, 1000, False),
        (42.0, 1200, True),
        (49.0, 1400, True),
        (52.0, 1600, True),
        (56.0, 1750, True),
        (44.0, 1700, False),
        (30.0, 600, False),
    ]:
        temp, gas, motion = phase
        score, level = score_for(temp, gas, motion)
        packets.append(Packet("001", temp, gas, motion, score, level))
    return packets


def scenario_false_alarm() -> list[Packet]:
    packets: list[Packet] = []
    for temp, gas, motion in [
        (24.0, 300, False),
        (26.0, 500, False),
        (27.0, 460, True),
        (28.0, 520, False),
        (29.0, 510, False),
        (25.0, 450, False),
    ]:
        score, level = score_for(temp, gas, motion)
        packets.append(Packet("002", temp, gas, motion, score, level))
    return packets


def scripted_scenarios() -> list[Packet]:
    return scenario_fire_drill() + scenario_false_alarm()
