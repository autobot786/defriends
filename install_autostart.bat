@echo off
:: ---------------------------------------------------------------------------
:: defriends Auto-Start Service Installer
::
:: Registers a Windows Scheduled Task that starts the defriends platform
:: automatically at user logon. After installation, the dashboard is always
:: accessible at http://127.0.0.1:8080/ui without running any commands.
::
:: Run this script ONCE as Administrator:
::   Right-click -> Run as Administrator
:: ---------------------------------------------------------------------------
setlocal EnableDelayedExpansion
title defriends - Auto-Start Installer

echo.
echo   ===============================================
echo     defriends Auto-Start Installer
echo   ===============================================
echo.

:: --- Check for Administrator privileges ---
net session >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] This script must be run as Administrator.
    echo           Right-click and select "Run as administrator".
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"
set "INSTALL_DIR=%~dp0"

:: --- Resolve Python to an ABSOLUTE path ---
:: The VBS startup script runs outside the user shell so it needs a full path.
set "PY_ABS="

:: Check PATH-accessible python and resolve to absolute
for %%C in (python python3 py) do (
    if not defined PY_ABS (
        for /f "delims=" %%P in ('where %%C 2^>nul') do (
            if not defined PY_ABS (
                set "PY_ABS=%%P"
            )
        )
    )
)

:: Check user venv
if not defined PY_ABS (
    if exist "C:\Users\%USERNAME%\.venv\Scripts\python.exe" (
        set "PY_ABS=C:\Users\%USERNAME%\.venv\Scripts\python.exe"
    )
)

:: Check common Windows install locations
if not defined PY_ABS (
    for /d %%D in ("C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python3*") do (
        if not defined PY_ABS (
            if exist "%%D\python.exe" set "PY_ABS=%%D\python.exe"
        )
    )
)

if not defined PY_ABS (
    echo   [ERROR] Python 3 not found.
    echo           Install Python 3.11+ and ensure it is in PATH or at:
    echo             C:\Users\%USERNAME%\.venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

echo   [OK] Python: !PY_ABS!
for /f "delims=" %%V in ('"!PY_ABS!" --version 2^>^&1') do echo   [OK] %%V

:: --- Install dependencies ---
echo   [..] Checking dependencies...
"!PY_ABS!" -c "import fastapi, uvicorn, pydantic, yaml, jsonschema, reportlab, httpx" >nul 2>&1
if errorlevel 1 (
    echo   [..] Installing dependencies...
    "!PY_ABS!" -m pip install -r requirements.txt --quiet
    if exist "packages\common\pyproject.toml" (
        "!PY_ABS!" -m pip install -e packages/common --quiet
    )
    echo   [OK] Dependencies installed.
) else (
    echo   [OK] All packages already installed.
)

:: --- Kill any existing defriends server on port 8080 ---
echo   [..] Checking for existing server on port 8080...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8080 " ^| findstr "LISTENING" 2^>nul') do (
    echo   [..] Stopping existing process PID=%%P
    taskkill /PID %%P /F >nul 2>&1
)

:: --- Create the startup VBS script ---
echo   [..] Creating startup script with absolute Python path...

set "VBS_PATH=%INSTALL_DIR%autostart_dirtybots.vbs"

> "!VBS_PATH!" (
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.CurrentDirectory = "%INSTALL_DIR%"
    echo WshShell.Environment^("Process"^).Item^("DIRTYBOT_MAPPING_PACK"^) = "%INSTALL_DIR%rules\mapping\mitre_cwe_context.v1.yaml"
    echo WshShell.Environment^("Process"^).Item^("DIRTYBOT_REPORT_SCHEMA"^) = "%INSTALL_DIR%schemas\report.schema.json"
    echo WshShell.Environment^("Process"^).Item^("DIRTYBOT_ORG_ID"^) = "demo-org"
    echo WshShell.Environment^("Process"^).Item^("PORT"^) = "8080"
    echo WshShell.Run """!PY_ABS!"" -m uvicorn app_unified:app --host 127.0.0.1 --port 8080", 0, False
)

echo   [OK] Created: !VBS_PATH!

:: --- Register Scheduled Task ---
echo   [..] Registering auto-start task...

schtasks /Delete /TN "defriends Platform" /F >nul 2>&1
schtasks /Create /TN "defriends Platform" /TR "wscript.exe \"!VBS_PATH!\"" /SC ONLOGON /RL HIGHEST /F >nul 2>&1

if errorlevel 1 (
    echo   [WARN] Could not create scheduled task.
) else (
    echo   [OK] Scheduled task "defriends Platform" registered.
)

:: --- Start the server NOW ---
echo.
echo   [..] Starting defriends server on port 8080...
start "" wscript.exe "!VBS_PATH!"

:: --- Wait and verify with retry loop ---
echo   [..] Waiting for server to start...
set "SERVER_OK=0"
for /L %%I in (1,1,10) do (
    if !SERVER_OK! EQU 0 (
        timeout /t 1 /nobreak >nul
        "!PY_ABS!" -c "import httpx;r=httpx.get('http://127.0.0.1:8080/health',timeout=2);exit(0 if r.status_code==200 else 1)" >nul 2>&1
        if not errorlevel 1 set "SERVER_OK=1"
    )
)

if !SERVER_OK! EQU 1 (
    echo   [OK] Server is running!
) else (
    echo   [WARN] Server may still be starting. Check: http://127.0.0.1:8080/health
)

echo.
echo   ===============================================
echo     defriends Auto-Start Installation Complete
echo   ===============================================
echo.
echo   Dashboard: http://127.0.0.1:8080/ui
echo   API Docs:  http://127.0.0.1:8080/docs
echo   Health:    http://127.0.0.1:8080/health
echo.
echo   Python:    !PY_ABS!
echo.
echo   The server starts automatically when you log in.
echo   To uninstall: schtasks /Delete /TN "defriends Platform" /F
echo.

start http://127.0.0.1:8080/ui

pause
