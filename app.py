from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_cors import CORS

# Resolve project paths
BASE_DIR = Path(__file__).resolve().parent
EDGE_NODE_DIR = BASE_DIR / "edge-fusion-node"
if str(EDGE_NODE_DIR) not in sys.path:
    sys.path.insert(0, str(EDGE_NODE_DIR))

# Dashboard static files directory
DASHBOARD_DIR = EDGE_NODE_DIR / "dashboard"
if not DASHBOARD_DIR.exists():
    DASHBOARD_DIR = BASE_DIR / "dashboard"

# Database path resolution (support serverless /tmp on Vercel)
def get_db_path() -> Path:
    if os.environ.get("VERCEL"):
        tmp_db = Path(tempfile.gettempdir()) / "data.db"
        seed_db = EDGE_NODE_DIR / "gateway" / "data.db"
        if not tmp_db.exists() and seed_db.exists():
            try:
                shutil.copyfile(seed_db, tmp_db)
            except Exception:
                pass
        return tmp_db
    
    local_db = EDGE_NODE_DIR / "gateway" / "data.db"
    if local_db.parent.exists():
        return local_db
    return BASE_DIR / "data.db"

DB_PATH = get_db_path()

# Initialize Flask application
app = Flask(__name__)
CORS(app)


def ensure_db() -> None:
    db_file = get_db_path()
    try:
        conn = sqlite3.connect(db_file)
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
    except Exception as e:
        print(f"[app] ensure_db error: {e}")


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


@app.before_request
def startup_event():
    ensure_db()


@app.route("/")
def index():
    if DASHBOARD_DIR.exists():
        return send_from_directory(str(DASHBOARD_DIR), "index.html")
    return jsonify({"status": "ok", "message": "Resilient Edge-Fusion Node Backend"})


@app.route("/dashboard")
def dashboard_redirect():
    return redirect("/dashboard/")


@app.route("/dashboard/")
def dashboard_root():
    if DASHBOARD_DIR.exists():
        return send_from_directory(str(DASHBOARD_DIR), "index.html")
    return jsonify({"status": "error", "message": "Dashboard not found"}), 404


@app.route("/dashboard/<path:filename>")
def dashboard_files(filename: str):
    if DASHBOARD_DIR.exists():
        return send_from_directory(str(DASHBOARD_DIR), filename)
    return jsonify({"status": "error", "message": "File not found"}), 404


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/latest")
def latest():
    try:
        db_file = get_db_path()
        conn = sqlite3.connect(db_file)
        rows = conn.execute(
            "SELECT node_id, temperature, gas_raw, score, level, motion, timestamp FROM readings ORDER BY id DESC LIMIT 200"
        ).fetchall()
        conn.close()
        payload = {
            "items": [
                {
                    "node_id": row[0],
                    "temperature": row[1],
                    "gas_raw": row[2],
                    "score": row[3],
                    "level": row[4],
                    "motion": bool(row[5]),
                    "timestamp": row[6],
                }
                for row in rows
            ]
        }
        return jsonify(payload)
    except Exception as e:
        return jsonify({"items": [], "error": str(e)})


@app.route("/nodes")
def nodes():
    try:
        db_file = get_db_path()
        conn = sqlite3.connect(db_file)
        rows = conn.execute(
            "SELECT node_id, MAX(score) AS score, MAX(timestamp) AS timestamp FROM readings GROUP BY node_id ORDER BY node_id"
        ).fetchall()
        conn.close()
        return jsonify(
            {
                "nodes": [
                    {"node_id": row[0], "score": row[1], "timestamp": row[2]}
                    for row in rows
                ]
            }
        )
    except Exception as e:
        return jsonify({"nodes": [], "error": str(e)})


@app.route("/api/telemetry", methods=["POST"])
def ingest_telemetry():
    data = request.get_json(silent=True) or {}
    packet = data.get("packet", "")
    parsed = parse_packet(packet) if packet else None
    if not parsed:
        return jsonify({"status": "error", "message": "Invalid packet"}), 400

    try:
        db_file = get_db_path()
        conn = sqlite3.connect(db_file)
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
        return jsonify({"status": "ok", "stored": parsed})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    ensure_db()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
