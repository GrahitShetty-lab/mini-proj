from __future__ import annotations

import os
import sqlite3
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from flask import Flask, jsonify, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tempfile

def get_db_path() -> Path:
    if os.environ.get("VERCEL"):
        tmp_db = Path(tempfile.gettempdir()) / "data.db"
        orig_db = Path(__file__).resolve().parent / "data.db"
        if not tmp_db.exists() and orig_db.exists():
            import shutil
            try:
                shutil.copyfile(orig_db, tmp_db)
            except Exception:
                pass
        return tmp_db
    return Path(__file__).resolve().parent / "data.db"


DB_PATH = get_db_path()
DASHBOARD_DIR = ROOT / "dashboard"
APP = Flask(__name__)


def ensure_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            temperature REAL,
            gas_raw INTEGER,
            score REAL,
            level TEXT,
            motion INTEGER,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def parse_packet(packet: str) -> dict[str, Any] | None:
    try:
        fields = packet.strip().split("|")
        parsed: dict[str, Any] = {}
        for field in fields:
            if not field or ":" not in field:
                continue
            key, value = field.split(":", 1)
            parsed[key] = value
        if "ID" not in parsed:
            return None
        temp = float(parsed.get("T", "0"))
        gas = int(float(parsed.get("G", "0")))
        score = float(parsed.get("SCORE", "0"))
        level = str(parsed.get("LVL", "NORMAL")).upper()
        motion = 1 if parsed.get("M") == "1" else 0
        return {
            "node_id": parsed["ID"],
            "temperature": temp,
            "gas_raw": gas,
            "score": score,
            "level": level,
            "motion": motion,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
    except (TypeError, ValueError):
        return None


class LoRaPacketSource:
    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError


class SerialLoRaSource(LoRaPacketSource):
    """Read packets from a serial USB device or a local file when no hardware is present."""

    def __init__(self, port: str = "/dev/ttyUSB0"):
        self.port = port

    def __iter__(self) -> Iterator[str]:
        while True:
            if os.path.exists(self.port):
                try:
                    with open(self.port, "r", encoding="utf-8") as handle:
                        for line in handle:
                            raw = line.strip()
                            if raw:
                                yield raw
                except OSError:
                    pass
            time.sleep(0.5)


class SimulatedSource(LoRaPacketSource):
    """Read packets from a local simulation log file, one packet per line."""

    def __init__(self, path: str | os.PathLike[str] | None = None):
        self.path = Path(path) if path else ROOT / "simulator" / "telemetry.log"
        self._last_size = 0

    def __iter__(self) -> Iterator[str]:
        while True:
            if self.path.exists():
                try:
                    with open(self.path, "r", encoding="utf-8") as handle:
                        lines = handle.read().splitlines()
                    if len(lines) > self._last_size:
                        new_lines = lines[self._last_size:]
                        for line in new_lines:
                            stripped = line.strip()
                            if stripped:
                                print(f"[gateway] SimulatedSource received: {stripped}")
                                yield stripped
                        self._last_size = len(lines)
                except OSError:
                    pass
            time.sleep(0.25)


class GatewayReceiver:
    def __init__(self, source: LoRaPacketSource | None = None):
        self.source = source or SimulatedSource()
        self._lock = threading.Lock()

    def ingest_packet(self, packet: str):
        if not packet or not packet.strip():
            return
        parsed = parse_packet(packet)
        if not parsed:
            print(f"[gateway] malformed packet ignored: {packet}")
            return
        print(f"[gateway] storing packet for {parsed['node_id']}: score={parsed['score']} level={parsed['level']}")
        with self._lock:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO readings (node_id, temperature, gas_raw, score, level, motion, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    parsed["node_id"],
                    parsed["temperature"],
                    parsed["gas_raw"],
                    parsed["score"],
                    parsed["level"],
                    parsed["motion"],
                    parsed["timestamp"],
                ),
            )
            conn.commit()
            conn.close()

    def run(self):
        for packet in self.source:
            try:
                self.ingest_packet(packet)
            except Exception:
                continue


@APP.before_request
def startup_event():
    ensure_db()


@APP.route("/dashboard/")
def dashboard_root():
    return send_from_directory(str(DASHBOARD_DIR), "index.html")


@APP.route("/dashboard/<path:filename>")
def dashboard_files(filename):
    return send_from_directory(str(DASHBOARD_DIR), filename)


@APP.route("/health")
def health():
    return jsonify({"status": "ok"})


@APP.route("/latest")
def latest():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT node_id, temperature, gas_raw, score, level, motion, timestamp FROM readings ORDER BY id DESC LIMIT 200"
    ).fetchall()
    conn.close()
    payload = {"items": [{
        "node_id": row[0],
        "temperature": row[1],
        "gas_raw": row[2],
        "score": row[3],
        "level": row[4],
        "motion": bool(row[5]),
        "timestamp": row[6],
    } for row in rows]}
    print(f"[gateway] /latest returned {len(payload['items'])} rows")
    return jsonify(payload)


@APP.route("/nodes")
def nodes():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT node_id, MAX(score) AS score, MAX(timestamp) AS timestamp FROM readings GROUP BY node_id ORDER BY node_id"
    ).fetchall()
    conn.close()
    return jsonify({"nodes": [{"node_id": row[0], "score": row[1], "timestamp": row[2]} for row in rows]})


def main():
    ensure_db()
    source = SimulatedSource()
    receiver = GatewayReceiver(source)
    thread = threading.Thread(target=receiver.run, daemon=True)
    thread.start()
    APP.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
