"""Fusion-score logic for the edge node.

The score combines normalized contributions from temperature, gas/smoke ADC,
and PIR motion into a 0..100 percentage value, using the same thresholds as the
original device firmware.
"""

from __future__ import annotations

from .config import (
    CRITICAL_THRESHOLD,
    GAS_BASE_RAW,
    GAS_WARNING_RAW,
    MAX_FUSION_SCORE,
    MOTION_BONUS,
    TEMP_BASE_C,
    TEMP_WARNING_C,
    WARNING_THRESHOLD,
)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def calculate_fusion_score(temperature_c: float, gas_raw: int, motion_detected: bool) -> float:
    """Return a fused 0..100 score from sensor inputs.

    Rules from the original firmware:
    - Temperature contributes full weight scaling from 30°C to 45°C.
    - Gas contributes full weight scaling from 500 to 1500 ADC.
    - Motion adds a flat +20% when triggered.
    - WARNING = 40%
    - CRITICAL = 75%
    """

    temp_component = 0.0
    if temperature_c >= TEMP_WARNING_C:
        temp_component = 100.0
    elif temperature_c > TEMP_BASE_C:
        temp_component = ((temperature_c - TEMP_BASE_C) / (TEMP_WARNING_C - TEMP_BASE_C)) * 100.0

    gas_component = 0.0
    if gas_raw >= GAS_WARNING_RAW:
        gas_component = 100.0
    elif gas_raw > GAS_BASE_RAW:
        gas_component = ((gas_raw - GAS_BASE_RAW) / (GAS_WARNING_RAW - GAS_BASE_RAW)) * 100.0

    motion_component = MOTION_BONUS if motion_detected else 0.0
    score = temp_component + gas_component + motion_component
    score = _clamp(score, 0.0, MAX_FUSION_SCORE)
    return round(score, 2)


def score_to_level(score: float) -> str:
    if score >= CRITICAL_THRESHOLD:
        return "CRITICAL"
    if score >= WARNING_THRESHOLD:
        return "WARNING"
    return "NORMAL"
