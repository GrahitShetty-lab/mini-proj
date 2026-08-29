from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulator.scenario import scripted_scenarios

SIM_LOG = ROOT / "simulator" / "telemetry.log"


def main():
    SIM_LOG.parent.mkdir(parents=True, exist_ok=True)
    if SIM_LOG.exists():
        SIM_LOG.unlink()

    packets = scripted_scenarios()
    print(f"Writing simulated packets to {SIM_LOG}")
    with open(SIM_LOG, "w", encoding="utf-8") as handle:
        for packet in packets:
            payload = packet.render()
            handle.write(payload + "\n")
            handle.flush()
            print(payload)
            time.sleep(1.5)


if __name__ == "__main__":
    main()
