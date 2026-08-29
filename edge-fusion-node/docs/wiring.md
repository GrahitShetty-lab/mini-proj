# Wiring and Pinout (ESP32)

This table matches the expected design for the Resilient Edge-Fusion Node.

| Device | ESP32 GPIO | Notes |
| --- | --- | --- |
| DHT22 data | 4 | Digital input; sensor reads temperature and humidity |
| MQ-2 analog output | 36 | Analog gas/smoke input |
| PIR HC-SR501 OUT | 23 | Motion detection input |
| RGB LED R | 26 | Active-low or active-high depending on LED driver |
| RGB LED G | 25 | Active-low or active-high depending on LED driver |
| RGB LED B | 33 | Active-low or active-high depending on LED driver |
| Buzzer | 27 | Audible alarm output |
| LoRa NSS/CS | 18 | SX1276 chip select |
| LoRa RESET | 14 | Module reset |
| LoRa DIO0/IRQ | 26 | Interrupt pin for receive/tx events |

The firmware constants live in `firmware/config.py` and are intentionally named rather than embedded as magic numbers. The fusion-score thresholds are:

- WARNING threshold: 40%
- CRITICAL threshold: 75%
- Temperature scaling: from 30°C to 45°C, full weight from 45°C upward
- Gas scaling: from 500 raw ADC to 1500 raw ADC, full weight from 1500 upward
- Motion bonus: +20% when triggered
