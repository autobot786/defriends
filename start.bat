@echo off
setlocal EnableDelayedExpansion
title defriends - Security Assessment Platform

cd /d "%~dp0"

echo.
echo   ===============================================
echo     defriends - Security Assessment Platform
echo   ===============================================
echo.

:: --- Resolve Python (absolute path) ---
set "PY="
for %%C in (python python3 py) do (
    if not defined PY (
        for /f "delims=" %%P in ('where %%C 2^>nul') do (
            if not defined PY set "PY=%%P"
        )
    )
)
if not defined PY (
    if exist "C:\Users\%USERNAME%\.venv\Scripts\python.exe" (
        set "PY=C:\Users\%USERNAME%\.venv\Scripts\python.exe"
    )
)
if not defined PY (
    for /d %%D in ("C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python3*") do (
        if not defined PY (
            if exist "%%D\python.exe" set "PY=%%D\python.exe"
        )
    )
)
if not defined PY (
    echo   [ERROR] Python 3 not found. Install Python 3.11+ and add it to PATH.
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%V in ('"!PY!" --version 2^>^&1') do echo   [OK] %%V found.
echo          Path: !PY!

:: --- Install dependencies ---
%PY% -c "import fastapi, uvicorn, pydantic, yaml, jsonschema, reportlab" >nul 2>&1
if errorlevel 1 (
    echo   [..] Installing dependencies...
    %PY% -m pip install -r requirements.txt --quiet
    if exist "packages\common\pyproject.toml" (
        %PY% -m pip install -e packages/common --quiet
    )
    echo   [OK] Dependencies installed.
) else (
    echo   [OK] All packages already installed.
)

:: --- Set environment variables ---
set "DIRTYBOT_MAPPING_PACK=%~dp0rules\mapping\mitre_cwe_context.v1.yaml"
set "DIRTYBOT_REPORT_SCHEMA=%~dp0schemas\report.schema.json"
if not defined DIRTYBOT_ORG_ID set "DIRTYBOT_ORG_ID=demo-org"

echo.
echo   -------------------------------------------------
echo    Dashboard : http://127.0.0.1:8080/ui
echo    API Docs  : http://127.0.0.1:8080/docs
echo    Health    : http://127.0.0.1:8080/health
echo   -------------------------------------------------
echo.
echo   Press Ctrl+C to stop the server.
echo.

:: --- Open browser after 2 seconds ---
start /b cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8080/ui"

:: --- Start the server ---
%PY% -m uvicorn app_unified:app --host 127.0.0.1 --port 8080 --reload
