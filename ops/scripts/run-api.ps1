# ops\scripts\run-api.ps1
param(
  [string]$RepoRoot = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1",
  [string]$Host     = "127.0.0.1",
  [int]   $_Port    = 8001
)

$ErrorActionPreference = "Stop"

# Single-instance mutex (process-local file lock)
$mutexFile = Join-Path $RepoRoot "ops\run-api.lock"
$fs = [System.IO.File]::Open($mutexFile, 'OpenOrCreate', 'ReadWrite', 'None')

# Paths
$VenvPy = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$LogDir = Join-Path $RepoRoot "ops\logs"
$null = New-Item -ItemType Directory -Force -Path $LogDir

# Ensure .env exists and expose key to process env
$envPath = Join-Path $RepoRoot ".env"
if (-not (Test-Path $envPath)) { throw ".env missing at $envPath" }
$SENTINEL_API_KEY = (Get-Content $envPath | ? {$_ -match '^SENTINEL_API_KEY='}) -replace '^SENTINEL_API_KEY=',''
if (-not $SENTINEL_API_KEY) { throw "SENTINEL_API_KEY not set in .env" }
$env:SENTINEL_API_KEY = $SENTINEL_API_KEY

# Kill any prior uvicorn on this port
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  ? { $_ .CommandLine -match "uvicorn.*$Host.*$_Port" } |
  % { Stop-Process -Id $_ .ProcessId -Force -ErrorAction SilentlyContinue }

# Log file
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss')
$log   = Join-Path $LogDir "api-$stamp.log"

# Launch uvicorn in the repo root
Push-Location $RepoRoot
& $VenvPy -m uvicorn sentinel_engine.api:app --host $Host --port $_Port --log-level info *>&1 |
  Tee-Object -FilePath $log
