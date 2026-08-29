import os
import sys
from pathlib import Path

# Add edge-fusion-node to sys.path so modules like gateway and firmware can be resolved
BASE_DIR = Path(__file__).resolve().parent
EDGE_NODE_DIR = BASE_DIR / "edge-fusion-node"
if str(EDGE_NODE_DIR) not in sys.path:
    sys.path.insert(0, str(EDGE_NODE_DIR))

from gateway.receiver import APP as app, DASHBOARD_DIR, ensure_db
from flask import send_from_directory, redirect

# Route root path to the web dashboard
@app.route("/")
def index():
    return send_from_directory(str(DASHBOARD_DIR), "index.html")

@app.route("/dashboard")
def dashboard_redirect():
    return redirect("/dashboard/")

if __name__ == "__main__":
    ensure_db()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
