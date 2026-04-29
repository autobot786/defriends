"""Root-level redirect -- delegates to the real app inside secmesh_scaffold/."""
import importlib.util
import os
import sys

_inner_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secmesh_scaffold")
if _inner_dir not in sys.path:
    sys.path.insert(0, _inner_dir)

_inner = os.path.join(_inner_dir, "app_unified.py")
_spec = importlib.util.spec_from_file_location("_app_unified_inner", _inner)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["_app_unified_inner"] = _mod
_spec.loader.exec_module(_mod)
app = _mod.app
