# Architecture

The data flow is intentionally simple and keeps decision-making at the edge.

1. The ESP32 node reads temperature, gas, and motion locally.
2. The `firmware/fusion.py` logic computes a weighted score from the raw sensor values.
3. The node publishes a compact LoRa payload: `ID:001|T:..|G:..|SCORE:..|LVL:..`.
4. The gateway receiver listens for packets, validates them, stores them in SQLite, and exposes them over a local HTTP API.
5. The dashboard polls the API and renders a live status view in the browser.

This architecture matters because it keeps the sensor safety logic close to the source: the node can react immediately with local LED and buzzer feedback even when the network is unavailable. LoRa is used only for distribution to nearby peers or a central base station, not for cloud dependence.
