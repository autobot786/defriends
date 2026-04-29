from __future__ import annotations
from typing import Any

def get_path(d: dict[str, Any], path: str, default: Any = None) -> Any:
    """Get a dotted path from nested dicts."""
    cur: Any = d
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur
