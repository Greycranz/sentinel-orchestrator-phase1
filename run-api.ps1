$ErrorActionPreference = 'Stop'

$RepoRoot = 'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1'
$EnvPath  = Join-Path $RepoRoot '.env'
$VenvPy   = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$LogsDir  = Join-Path $RepoRoot 'ops\logs'
$ApiLog   = Join-Path $LogsDir ('api-' + (Get-Date).ToString('yyyyMMdd-HHmmss') + '.log')

if (!(Test-Path $LogsDir)) { New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null }

# Ensure .env (so auth guard works)
if (!(Test-Path $EnvPath)) {
  'SENTINEL_API_KEY=super-secret-change-me' | Set-Content -Path $EnvPath -Encoding UTF8
}

# Ensure venv + deps
if (!(Test-Path $VenvPy)) {
  if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 -m venv (Join-Path $RepoRoot '.venv')
  } elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python -m venv (Join-Path $RepoRoot '.venv')
  } else {
    throw 'No Python found on PATH.'
  }
}
& $VenvPy -m pip install --quiet --disable-pip-version-check `
  'fastapi==0.110.*' 'uvicorn[standard]==0.30.*' 'sqlalchemy==2.0.*' 'pydantic==2.*' | Out-Null

# Kill any old uvicorn on port 8001
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'uvicorn.*127\.0\.0\.1.*8001' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

# Run inline so NSSM stays attached; append logs
Set-Location $RepoRoot
& $VenvPy -m uvicorn 'sentinel_engine.api:app' --host 127.0.0.1 --port 8001 --log-level info --env-file .env *>> $ApiLog
