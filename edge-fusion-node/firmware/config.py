"""Named configuration values for the edge-fusion node.

These values must remain consistent with the original firmware behavior and the
rest of the demo stack.
"""

from __future__ import annotations

# Hardware pin assignments for an ESP32.
PIN_DHT22 = 4
PIN_MQ2 = 36
PIN_PIR = 23
PIN_RGB_RED = 26
PIN_RGB_GREEN = 25
PIN_RGB_BLUE = 33
PIN_BUZZER = 27

# Sensor thresholds and ranges.
TEMP_WARNING_C = 45.0
TEMP_BASE_C = 30.0
GAS_WARNING_RAW = 1500
GAS_BASE_RAW = 500
MOTION_BONUS = 20.0
WARNING_THRESHOLD = 40.0
CRITICAL_THRESHOLD = 75.0
MAX_FUSION_SCORE = 100.0

# LoRa defaults.
LORA_BAND = 915E6
LORA_CS_PIN = 18
LORA_RESET_PIN = 14
LORA_IRQ_PIN = 26
LORA_SF = 7
LORA_BW = 125000

# Runtime control.
MOCK_HARDWARE = True

# LED signals.
RGB_NORMAL = (0, 255, 0)
RGB_WARNING = (255, 165, 0)
RGB_CRITICAL = (255, 0, 0)
