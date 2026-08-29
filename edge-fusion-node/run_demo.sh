#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

python -m venv .venv >/dev/null 2>&1 || true
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
  . .venv/Scripts/activate
else
  echo "Python venv not found; create one with: python -m venv .venv"
  exit 1
fi

python -m pip install -r requirements.txt >/dev/null

python simulator/demo.py > /tmp/edge_fusion_simulator.log 2>&1 &
SIM_PID=$!
python gateway/receiver.py > /tmp/edge_fusion_gateway.log 2>&1 &
GW_PID=$!

trap "kill $SIM_PID $GW_PID 2>/dev/null || true" EXIT

echo "Simulator PID: $SIM_PID"
echo "Gateway PID: $GW_PID"
echo "Open http://localhost:8000/dashboard/"
wait
