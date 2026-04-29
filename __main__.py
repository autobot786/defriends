"""Allow running the defriends platform with:  python -m secmesh_scaffold  or  python ."""

from __future__ import annotations

import os
import sys
import webbrowser
import threading

def main() -> None:
    # Ensure we run from the correct directory
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    # Ensure *this* directory is first in sys.path so uvicorn's reloader
    # finds secmesh_scaffold/app_unified.py, not an empty stub at the repo root.
    if here not in sys.path:
        sys.path.insert(0, here)

    # Set required environment variables if not already set
    os.environ.setdefault(
        "DIRTYBOT_MAPPING_PACK",
        os.path.join(here, "rules", "mapping", "mitre_cwe_context.v1.yaml"),
    )
    os.environ.setdefault(
        "DIRTYBOT_REPORT_SCHEMA",
        os.path.join(here, "schemas", "report.schema.json"),
    )
    os.environ.setdefault("DIRTYBOT_ORG_ID", "demo-org")

    host = "127.0.0.1"
    port = int(os.environ.get("PORT", "8080"))

    print()
    print("  ===============================================")
    print("    defriends - Security Assessment Platform")
    print("  ===============================================")
    print()
    print(f"   Dashboard : http://{host}:{port}/ui")
    print(f"   API Docs  : http://{host}:{port}/docs")
    print(f"   Health    : http://{host}:{port}/health")
    print()
    print("  Press Ctrl+C to stop the server.")
    print()

    # Open browser after a short delay
    url = f"http://{host}:{port}/ui"
    threading.Timer(2.0, lambda: webbrowser.open(url)).start()

    try:
        import uvicorn
    except ImportError:
        print("  [ERROR] uvicorn not installed. Run:  pip install -r requirements.txt")
        sys.exit(1)

    uvicorn.run(
        "app_unified:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
