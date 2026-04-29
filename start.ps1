#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launches the defriends Security Assessment Platform.
.DESCRIPTION
    Sets required environment variables, installs dependencies if needed,
    and starts the unified API server. The dashboard opens automatically
    in your default browser.
.EXAMPLE
    .\start.ps1
    .\start.ps1 -Port 9000
    .\start.ps1 -SkipInstall
#>
param(
    [int]$Port = 8080,
    [string]$Host = "127.0.0.1",
    [switch]$SkipInstall,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host ""
Write-Host "  ===============================================" -ForegroundColor Cyan
Write-Host "    defriends - Security Assessment Platform" -ForegroundColor Cyan
Write-Host "  ===============================================" -ForegroundColor Cyan
Write-Host ""

# --- Resolve Python executable (absolute path) ---
$py = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $found = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($found) {
            $ver = & $found.Source --version 2>&1
            if ($ver -match "Python 3\.") { $py = $found.Source; break }
        }
    } catch { }
}
# Fallback: check common venv and install locations
if (-not $py) {
    $fallbacks = @(
        "$env:USERPROFILE\.venv\Scripts\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    )
    foreach ($fb in $fallbacks) {
        if (Test-Path $fb) { $py = $fb; break }
    }
}
if (-not $py) {
    Write-Host "  [ERROR] Python 3 not found. Install Python 3.11+ and add it to PATH." -ForegroundColor Red
    Write-Host "          Or create a venv at: $env:USERPROFILE\.venv" -ForegroundColor Red
    Write-Host ""
    Read-Host "  Press Enter to exit"
    exit 1
}
Write-Host "  [OK] Python found: $(& $py --version 2>&1)" -ForegroundColor Green
Write-Host "       Path: $py" -ForegroundColor DarkGray

# --- Install dependencies ---
if (-not $SkipInstall) {
    Write-Host "  [..] Checking dependencies..." -ForegroundColor Yellow
    try {
        & $py -c "import fastapi, uvicorn, pydantic, yaml, jsonschema, reportlab" 2>$null
        Write-Host "  [OK] All packages already installed." -ForegroundColor Green
    } catch {
        Write-Host "  [..] Installing requirements..." -ForegroundColor Yellow
        & $py -m pip install -r requirements.txt --quiet
        if (Test-Path "packages\common\pyproject.toml") {
            & $py -m pip install -e packages/common --quiet
        }
        Write-Host "  [OK] Dependencies installed." -ForegroundColor Green
    }
}

# --- Set environment variables ---
$env:DIRTYBOT_MAPPING_PACK  = Join-Path $ScriptDir "rules\mapping\mitre_cwe_context.v1.yaml"
$env:DIRTYBOT_REPORT_SCHEMA = Join-Path $ScriptDir "schemas\report.schema.json"
if (-not $env:DIRTYBOT_ORG_ID) { $env:DIRTYBOT_ORG_ID = "demo-org" }

Write-Host ""
Write-Host "  Mapping Pack : $env:DIRTYBOT_MAPPING_PACK" -ForegroundColor DarkGray
Write-Host "  Report Schema: $env:DIRTYBOT_REPORT_SCHEMA" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  -------------------------------------------------" -ForegroundColor DarkGray
Write-Host "   Dashboard : http://${Host}:${Port}/ui" -ForegroundColor White
Write-Host "   API Docs  : http://${Host}:${Port}/docs" -ForegroundColor White
Write-Host "   Health    : http://${Host}:${Port}/health" -ForegroundColor White
Write-Host "  -------------------------------------------------" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server." -ForegroundColor DarkGray
Write-Host ""

# --- Open browser after a short delay ---
if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($url)
        Start-Sleep -Seconds 2
        Start-Process $url
    } -ArgumentList "http://${Host}:${Port}/ui" | Out-Null
}

# --- Start the server ---
& $py -m uvicorn app_unified:app --host $Host --port $Port --reload
