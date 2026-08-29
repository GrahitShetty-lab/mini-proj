from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulator.scenario import scenario_false_alarm, scenario_fire_drill

LOG_PATH = ROOT / "simulator" / "telemetry.log"


def write_packet_line(packet: str) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as handle:
        handle.write(packet + "\n")
        handle.flush()


def stream_scenarios() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists():
        LOG_PATH.unlink()

    scenarios = [
        ("fire drill", scenario_fire_drill()),
        ("false alarm", scenario_false_alarm()),
    ]

    print(f"[simulator] log path: {LOG_PATH}")
    for label, packets in scenarios:
        print(f"[simulator] starting {label}")
        for packet in packets:
            payload = packet.render()
            write_packet_line(payload)
            print(f"[simulator] wrote {payload}")
            time.sleep(1.5)


def main() -> None:
    stream_scenarios()


if __name__ == "__main__":
    main()
