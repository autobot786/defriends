"""defriends — unified FastAPI application.

Public routes  : /  (landing)  /login  /health  /api
Protected routes: /ui  /docs  /user  /v1/masterpiece/manifest
Auth endpoints  : /v1/auth/register  /v1/auth/login  /v1/auth/logout
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from pathlib import Path
from typing import Optional

from fastapi import Cookie, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(docs_url=None, redoc_url=None)

_HERE = Path(__file__).parent
_STATIC = _HERE / "static"

app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

# ---------------------------------------------------------------------------
# In-memory stores  (demo only — not for production)
# ---------------------------------------------------------------------------
# { email: {"name": ..., "hashed_pw": ..., "role": ...} }
_USERS: dict[str, dict] = {}

# { session_token: email }
_SESSIONS: dict[str, str] = {}


_PBKDF2_ITERS = 260_000  # OWASP-recommended minimum for PBKDF2-HMAC-SHA256 (2023)


def _hash_pw(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    """Return (hex_hash, hex_salt) using PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = secrets.token_bytes(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERS)
    return dk.hex(), salt.hex()


def _verify_pw(password: str, stored_hash: str, stored_salt: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    candidate, _ = _hash_pw(password, bytes.fromhex(stored_salt))
    return hmac.compare_digest(candidate, stored_hash)


def _get_session_user(session_id: Optional[str]) -> Optional[dict]:
    """Return the user dict for an active session, or None."""
    if not session_id:
        return None
    email = _SESSIONS.get(session_id)
    if not email:
        return None
    return _USERS.get(email)


def _static(name: str) -> FileResponse:
    return FileResponse(_STATIC / name)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = "Demo User"
    role: str = "admin"


class LoginRequest(BaseModel):
    email: str
    password: str


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def landing():
    return _static("landing.html")


@app.get("/welcome", include_in_schema=False)
async def welcome():
    return _static("landing.html")


@app.get("/login", include_in_schema=False)
async def login_page(next: str = "/ui"):
    return _static("login.html")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "defriends"}


@app.get("/api")
async def api_index(session_id: Optional[str] = Cookie(default=None)):
    user = _get_session_user(session_id)
    if user:
        return {
            "service": "defriends API",
            "status": "authenticated",
            "user": user.get("email"),
            "role": user.get("role"),
            "ui": "/ui",
            "health": "/health",
        }
    return {
        "service": "defriends API",
        "status": "login_required",
        "login": "/login",
        "docs": "/login?next=/docs",
        "health": "/health",
    }


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------
@app.post("/v1/auth/register", status_code=201)
async def register(body: RegisterRequest):
    email = body.email.strip().lower()
    if email in _USERS:
        raise HTTPException(status_code=400, detail="Email already registered.")
    if len(body.password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters.")
    pw_hash, pw_salt = _hash_pw(body.password)
    # Clamp role to known values; default to 'user' for safety.
    allowed_roles = {"user", "admin", "viewer"}
    role = body.role if body.role in allowed_roles else "user"
    _USERS[email] = {
        "email": email,
        "name": body.name,
        "role": role,
        "pw_hash": pw_hash,
        "pw_salt": pw_salt,
    }
    return {"message": "User registered successfully.", "email": email}


@app.post("/v1/auth/login")
async def login(body: LoginRequest):
    email = body.email.strip().lower()
    user = _USERS.get(email)
    if not user or not _verify_pw(body.password, user["pw_hash"], user["pw_salt"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = secrets.token_urlsafe(32)
    _SESSIONS[token] = email
    # Detect HTTPS so we can set the Secure flag when appropriate.
    _secure = os.environ.get("HTTPS_ENABLED", "").lower() in ("1", "true", "yes")
    response = JSONResponse({"message": "Login successful.", "email": email})
    response.set_cookie(
        key="session_id",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=_secure,
    )
    return response


@app.post("/v1/auth/logout")
async def logout(session_id: Optional[str] = Cookie(default=None)):
    if session_id and session_id in _SESSIONS:
        del _SESSIONS[session_id]
    response = JSONResponse({"message": "Logged out."})
    response.delete_cookie("session_id")
    return response


# ---------------------------------------------------------------------------
# Protected routes — require login
# ---------------------------------------------------------------------------
def _auth_redirect(path: str):
    """Return a redirect to /login?next=<path> for unauthenticated users."""
    return RedirectResponse(url=f"/login?next={path}", status_code=302)


@app.get("/ui", include_in_schema=False)
async def dashboard(session_id: Optional[str] = Cookie(default=None)):
    if not _get_session_user(session_id):
        return _auth_redirect("/ui")
    return _static("dashboard.html")


@app.get("/docs", include_in_schema=False)
async def docs_page(session_id: Optional[str] = Cookie(default=None)):
    if not _get_session_user(session_id):
        return _auth_redirect("/docs")
    return JSONResponse(
        {
            "message": "API documentation is available to authenticated users only.",
            "note": "Interactive docs are intentionally disabled; see README for API reference.",
        }
    )


@app.get("/user", include_in_schema=False)
async def user_portal(session_id: Optional[str] = Cookie(default=None)):
    if not _get_session_user(session_id):
        return _auth_redirect("/user")
    user = _get_session_user(session_id)
    return JSONResponse({"email": user["email"], "name": user["name"], "role": user["role"]})


@app.get("/v1/masterpiece/manifest")
async def capability_manifest(session_id: Optional[str] = Cookie(default=None)):
    if not _get_session_user(session_id):
        raise HTTPException(status_code=401, detail="Authentication required.")
    return {
        "service": "defriends",
        "capabilities": [
            "ingestion", "normalizer", "mapping", "scoring",
            "reporting", "controls", "legitimacy", "ai_assistant",
        ],
    }
