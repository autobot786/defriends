#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# defriends Auto-Start Service Installer (macOS / Linux)
#
# Registers a persistent background service so the defriends platform starts
# automatically at login. After installation the dashboard is always
# accessible at http://127.0.0.1:8080/ui without running any commands.
#
# Usage (run once):
#   chmod +x install_autostart.sh
#   ./install_autostart.sh
#
# To uninstall:
#   macOS : launchctl unload ~/Library/LaunchAgents/com.dirtybots.platform.plist
#   Linux : systemctl --user disable --now dirtybots.service
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8080}"
HOST="127.0.0.1"

echo ""
echo "  ==============================================="
echo "    defriends Auto-Start Installer"
echo "  ==============================================="
echo ""

# --- Resolve Python ---
PY=""
for candidate in python3 python py; do
  if command -v "$candidate" &>/dev/null; then
    ver=$("$candidate" --version 2>&1 || true)
    if echo "$ver" | grep -q "Python 3\."; then
      PY="$(command -v "$candidate")"
      break
    fi
  fi
done

if [ -z "$PY" ]; then
  for fb in "$HOME/.venv/bin/python3" "$HOME/.venv/bin/python" "/usr/local/bin/python3" "/opt/homebrew/bin/python3"; do
    if [ -x "$fb" ]; then
      PY="$fb"
      break
    fi
  done
fi

if [ -z "$PY" ]; then
  echo "  [ERROR] Python 3 not found. Install Python 3.11+ and add it to PATH."
  exit 1
fi

PY="$(realpath "$PY" 2>/dev/null || readlink -f "$PY" 2>/dev/null || echo "$PY")"
echo "  [OK] Python: $PY ($($PY --version 2>&1))"

# --- Install dependencies ---
echo "  [..] Checking dependencies..."
if $PY -c "import fastapi, uvicorn, pydantic, yaml, jsonschema, reportlab" 2>/dev/null; then
  echo "  [OK] All packages already installed."
else
  echo "  [..] Installing requirements..."
  $PY -m pip install -r requirements.txt --quiet
  if [ -f "packages/common/pyproject.toml" ]; then
    $PY -m pip install -e packages/common --quiet
  fi
  echo "  [OK] Dependencies installed."
fi

# --- Kill any existing server on the port ---
echo "  [..] Checking for existing server on port $PORT..."
if command -v lsof &>/dev/null; then
  PID=$(lsof -ti :"$PORT" 2>/dev/null || true)
  if [ -n "$PID" ]; then
    echo "  [..] Stopping existing process PID=$PID"
    kill "$PID" 2>/dev/null || true
    sleep 1
  fi
fi

# --- Detect platform and install service ---
OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
  # ======================== macOS — LaunchAgent ========================
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_FILE="$PLIST_DIR/com.dirtybots.platform.plist"
  mkdir -p "$PLIST_DIR"

  cat > "$PLIST_FILE" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.dirtybots.platform</string>
  <key>ProgramArguments</key>
  <array>
    <string>${PY}</string>
    <string>-m</string>
    <string>uvicorn</string>
    <string>app_unified:app</string>
    <string>--host</string>
    <string>${HOST}</string>
    <string>--port</string>
    <string>${PORT}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>${SCRIPT_DIR}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>DIRTYBOT_MAPPING_PACK</key>
    <string>${SCRIPT_DIR}/rules/mapping/mitre_cwe_context.v1.yaml</string>
    <key>DIRTYBOT_REPORT_SCHEMA</key>
    <string>${SCRIPT_DIR}/schemas/report.schema.json</string>
    <key>DIRTYBOT_ORG_ID</key>
    <string>demo-org</string>
    <key>PORT</key>
    <string>${PORT}</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${SCRIPT_DIR}/dirtybots.log</string>
  <key>StandardErrorPath</key>
  <string>${SCRIPT_DIR}/dirtybots.log</string>
</dict>
</plist>
PLIST

  launchctl unload "$PLIST_FILE" 2>/dev/null || true
  launchctl load "$PLIST_FILE"
  echo "  [OK] LaunchAgent installed: $PLIST_FILE"
  echo "  [OK] Service will auto-start at login."
  echo ""
  echo "  To uninstall:"
  echo "    launchctl unload $PLIST_FILE"
  echo "    rm $PLIST_FILE"

else
  # ======================== Linux — systemd user service ========================
  SERVICE_DIR="$HOME/.config/systemd/user"
  SERVICE_FILE="$SERVICE_DIR/dirtybots.service"
  mkdir -p "$SERVICE_DIR"

  cat > "$SERVICE_FILE" <<SERVICE
[Unit]
Description=defriends Security Assessment Platform
After=network.target

[Service]
Type=simple
WorkingDirectory=${SCRIPT_DIR}
Environment=DIRTYBOT_MAPPING_PACK=${SCRIPT_DIR}/rules/mapping/mitre_cwe_context.v1.yaml
Environment=DIRTYBOT_REPORT_SCHEMA=${SCRIPT_DIR}/schemas/report.schema.json
Environment=DIRTYBOT_ORG_ID=demo-org
Environment=PORT=${PORT}
ExecStart=${PY} -m uvicorn app_unified:app --host ${HOST} --port ${PORT}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
SERVICE

  systemctl --user daemon-reload
  systemctl --user enable --now dirtybots.service
  echo "  [OK] systemd user service installed: $SERVICE_FILE"
  echo "  [OK] Service will auto-start at login."
  echo ""
  echo "  To uninstall:"
  echo "    systemctl --user disable --now dirtybots.service"
  echo "    rm $SERVICE_FILE"
fi

# --- Wait and verify ---
echo ""
echo "  [..] Waiting for server to start..."
SERVER_OK=0
for i in $(seq 1 10); do
  sleep 1
  if $PY -c "import urllib.request; urllib.request.urlopen('http://${HOST}:${PORT}/health', timeout=2)" 2>/dev/null; then
    SERVER_OK=1
    break
  fi
done

if [ "$SERVER_OK" -eq 1 ]; then
  echo "  [OK] Server is running!"
else
  echo "  [WARN] Server may still be starting. Check: http://${HOST}:${PORT}/health"
fi

echo ""
echo "  ==============================================="
echo "    defriends Auto-Start Installation Complete"
echo "  ==============================================="
echo ""
echo "  Dashboard: http://${HOST}:${PORT}/ui"
echo "  API Docs:  http://${HOST}:${PORT}/docs"
echo "  Health:    http://${HOST}:${PORT}/health"
echo ""
echo "  Python:    $PY"
echo ""
echo "  The server starts automatically when you log in."
echo ""

# --- Open browser ---
URL="http://${HOST}:${PORT}/ui"
if command -v open &>/dev/null; then
  open "$URL"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$URL"
fi
