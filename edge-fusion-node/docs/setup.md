# Setup and Run Guide

This repository supports two distinct modes:

- Simulation mode: run the full local demo on a laptop with no hardware attached.
- Hardware mode: flash the firmware to an actual ESP32 and attach the sensor and LoRa hardware.

Use the instructions below to tell which path you are on.

## A. Simulation mode (no hardware) — use this for the local demo

1. Open a terminal in the repo root.
2. Create and activate a virtual environment:

```bash
cd edge-fusion-node
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the demo stack:

```bash
./run_demo.sh
```

5. Open the dashboard in a browser:

```text
http://localhost:8000/dashboard/
```

6. The gateway API is available at:

```text
http://127.0.0.1:8001/latest
```

This path runs the simulator, gateway, and dashboard locally and is the correct choice when no ESP32 or LoRa hardware is connected.

## B. Real hardware mode (ESP32 + sensors + LoRa) — use this for deployment

Use this path only when the actual hardware is connected and you want the real node to transmit packets.

1. Install MicroPython on the ESP32.
2. Connect the ESP32 to your computer over USB.
3. Open Thonny and select the ESP32 board backend.
4. Copy the contents of `firmware/` to the device or save them as MicroPython files on the board.
5. Flash `firmware/main.py` as the main entrypoint. Ensure the package imports resolve correctly across `config.py`, `sensors.py`, `fusion.py`, `indicators.py`, and `lora_link.py`.
6. Confirm the serial monitor shows a live sensor cycle and that packets are broadcast on the LoRa link.
7. Connect the SX1276 LoRa module using the wiring table in `docs/wiring.md`.
8. Watch the gateway ingest the packets and the dashboard update on localhost.

## Notes

- The simulation path is offline-only: there is no cloud dependency and no external API call.
- The packet format used by both paths is: `ID:001|T:<temp>|G:<gas>|SCORE:<score>|LVL:<level>`
- If you are running `./run_demo.sh`, you are in simulation mode. If you are flashing `firmware/main.py` to an ESP32, you are in real hardware mode.
