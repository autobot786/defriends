#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# defriends - Security Assessment Platform (Cross-Platform Launcher)
#
# Works on macOS, Linux, and WSL.
# Usage:
#   chmod +x start.sh
#   ./start.sh
#   ./start.sh --port 9000
#   ./start.sh --no-browser
# ---------------------------------------------------------------------------
set -euo pipefail

PORT="${PORT:-8080}"
HOST="127.0.0.1"
SKIP_INSTALL=0
NO_BROWSER=0

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port)       PORT="$2"; shift 2 ;;
    --host)       HOST="$2"; shift 2 ;;
    --skip-install) SKIP_INSTALL=1; shift ;;
    --no-browser) NO_BROWSER=1; shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "  ==============================================="
echo "    defriends - Security Assessment Platform"
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

# Fallback: check common venv locations
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
  echo ""
  exit 1
fi

echo "  [OK] $($PY --version 2>&1) found."
echo "       Path: $PY"

# --- Install dependencies ---
if [ "$SKIP_INSTALL" -eq 0 ]; then
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
fi

# --- Set environment variables ---
export DIRTYBOT_MAPPING_PACK="$SCRIPT_DIR/rules/mapping/mitre_cwe_context.v1.yaml"
export DIRTYBOT_REPORT_SCHEMA="$SCRIPT_DIR/schemas/report.schema.json"
export DIRTYBOT_ORG_ID="${DIRTYBOT_ORG_ID:-demo-org}"

echo ""
echo "  Mapping Pack : $DIRTYBOT_MAPPING_PACK"
echo "  Report Schema: $DIRTYBOT_REPORT_SCHEMA"
echo ""
echo "  -------------------------------------------------"
echo "   Dashboard : http://${HOST}:${PORT}/ui"
echo "   API Docs  : http://${HOST}:${PORT}/docs"
echo "   Health    : http://${HOST}:${PORT}/health"
echo "  -------------------------------------------------"
echo ""
echo "  Press Ctrl+C to stop the server."
echo ""

# --- Open browser after a short delay ---
if [ "$NO_BROWSER" -eq 0 ]; then
  (
    sleep 2
    URL="http://${HOST}:${PORT}/ui"
    if command -v open &>/dev/null; then
      open "$URL"                 # macOS
    elif command -v xdg-open &>/dev/null; then
      xdg-open "$URL"            # Linux
    elif command -v wslview &>/dev/null; then
      wslview "$URL"             # WSL
    fi
  ) &
fi

# --- Start the server ---
exec $PY -m uvicorn app_unified:app --host "$HOST" --port "$PORT" --reload
