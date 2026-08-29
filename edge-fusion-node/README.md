# Resilient Edge-Fusion Node

A local, offline demo stack for a public-safety edge sensor node that fuses temperature, smoke/gas, and motion into a single score, relays it via LoRa, persists it in a gateway database, and renders it on a local dashboard.

## Quickstart

```bash
cd edge-fusion-node
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
./run_demo.sh
```

Then open:

- http://localhost:8000/dashboard/ to view the dashboard
- http://localhost:8001/health for the gateway health endpoint

## Components

- `firmware/`: MicroPython firmware modules for ESP32 and a CPython-compatible mock mode.
- `gateway/`: SQLite-persisted receiver and HTTP API.
- `dashboard/`: single-page web dashboard.
- `simulator/`: realistic telemetry generator for demo/testing.
- `docs/`: architecture and setup docs.

## Simulation mode

The repo is designed to run on a laptop with no hardware attached. The `simulator` feeds packets into the same gateway interface a real LoRa source would use, and the dashboard reads the gateway API locally.

## Real hardware

The firmware is structured so the same logic can be flashed to an ESP32. The LoRa interface is deliberately isolated behind a simple wrapper so a real SX1276 driver can be swapped in without changing control logic.
