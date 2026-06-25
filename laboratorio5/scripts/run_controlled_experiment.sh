#!/bin/sh
set -eu

node src/index.js &
SERVER_PID=$!

cleanup() {
  kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

python3 - <<'PY'
import time
import requests

deadline = time.time() + 30
last_error = None

while time.time() < deadline:
    try:
        response = requests.get("http://localhost:4000/rest/players/1", timeout=1)
        if response.status_code == 200:
            raise SystemExit(0)
        last_error = f"status {response.status_code}"
    except requests.RequestException as error:
        last_error = str(error)
    time.sleep(0.5)

raise SystemExit(f"API nao ficou pronta em 30s: {last_error}")
PY

python3 scripts/experiment.py
python3 scripts/analyze.py
python3 app/dashboard.py
