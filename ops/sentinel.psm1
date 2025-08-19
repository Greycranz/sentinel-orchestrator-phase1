Set-StrictMode -Version Latest

# Default repo root based on this module's folder (ops -> repo root)
$Script:Sentinel_DefaultRepoRoot = Split-Path $PSScriptRoot -Parent

function Get-SentinelConfig {
  param([string]$RepoRoot = $Script:Sentinel_DefaultRepoRoot)
  $Base = "http://127.0.0.1:8001"
  $keyLine = Get-Content (Join-Path $RepoRoot ".env") | ? { $_ -match '^SENTINEL_API_KEY=' } | Select-Object -First 1
  $Key = if ($keyLine) { $keyLine -replace '^SENTINEL_API_KEY=', '' } else { "" }
  return @{
    RepoRoot = $RepoRoot
    Base     = $Base
    Hdr      = @{ "X-API-Key" = $Key }
    PyExe    = (Join-Path $RepoRoot ".venv\Scripts\python.exe")
    WorkerPy = (Join-Path $RepoRoot "ops\agent_worker.py")
    StartPS1 = (Join-Path $RepoRoot "ops\Start-Sentinel.ps1")
    LogDir   = (Join-Path $RepoRoot "ops\logs")
  }
}

function Test-SentinelApi {
  $cfg = Get-SentinelConfig
  try { (Invoke-RestMethod "$($cfg.Base)/healthz" -TimeoutSec 2).status -eq 'ok' } catch { $false }
}

function Ensure-SentinelUp {
  $cfg = Get-SentinelConfig
  New-Item -ItemType Directory -Force $cfg.LogDir | Out-Null

  if (-not (Test-SentinelApi)) {
    # start API via Start-Sentinel.ps1 (hidden)
    Start-Process powershell.exe -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","`"$($cfg.StartPS1)`"" -WindowStyle Hidden | Out-Null
    foreach ($i in 1..20) { if (Test-SentinelApi) { break }; Start-Sleep -Milliseconds 750 }
  }

  # ensure worker process exists (our venv python running agent_worker.py)
  $running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    ? { $_.CommandLine -like "*ops*agent_worker.py*" -and $_.CommandLine -like "*\.venv\Scripts\python.exe*" }
  if (-not $running) {
    Start-Process -FilePath $cfg.PyExe -ArgumentList $cfg.WorkerPy -WorkingDirectory $cfg.RepoRoot -WindowStyle Hidden | Out-Null
  }
}

function Invoke-Sentinel {
  param([string]$Path, [string]$Method="GET", [object]$Body=$null)
  $cfg = Get-SentinelConfig
  if ($Method -eq "GET")  { return Invoke-RestMethod "$($cfg.Base)$Path" -Headers $cfg.Hdr }
  if ($Method -eq "POST") {
    if ($Body -ne $null) { return Invoke-RestMethod -Method POST "$($cfg.Base)$Path" -Headers $cfg.Hdr -ContentType "application/json" -Body ($Body | ConvertTo-Json) }
    else                 { return Invoke-RestMethod -Method POST "$($cfg.Base)$Path" -Headers $cfg.Hdr }
  }
  throw "Unsupported method: $Method"
}

function Sentinel-Totals       { Invoke-Sentinel "/v0/jobs/totals" | ConvertTo-Json -Compress }
function Sentinel-Recent       { param([int]$Limit=10) Invoke-Sentinel "/v0/jobs/recent?limit=$Limit" | ConvertTo-Json -Depth 6 }
function Sentinel-GetJob       { param([int]$Id) Invoke-Sentinel "/v0/jobs/get/$Id" | ConvertTo-Json -Depth 6 }
function Sentinel-EnqueueEcho  { param([string]$Msg="hello") Invoke-Sentinel "/v0/jobs/enqueue" "POST" @{ kind="echo"; payload=@{ msg=$Msg } } }
function Sentinel-EnqueueHttp  { param([string]$Url="https://httpbin.org/get",[string]$Method="GET") Invoke-Sentinel "/v0/jobs/enqueue" "POST" @{ kind="http"; payload=@{ method=$Method; url=$Url } } }
function Sentinel-UnblockStuck { param([int]$AgeSeconds=300) Invoke-Sentinel "/v0/jobs/unblock_stuck?age_seconds=$AgeSeconds" "POST" }

function Sentinel-Status {
  $cfg = Get-SentinelConfig
  [pscustomobject]@{
    ApiHealthy = Test-SentinelApi
    WorkerProc = (Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? { $_.CommandLine -like "*ops*agent_worker.py*" } | Select-Object -First 1) -ne $null
    Logs       = @{
      ApiOut = Join-Path $cfg.LogDir "uvicorn.out.log"
      ApiErr = Join-Path $cfg.LogDir "uvicorn.err.log"
      Worker = Join-Path $cfg.RepoRoot "ops\logs\agent_worker.log"
    }
  } | ConvertTo-Json -Depth 5
}

Export-ModuleMember -Function Get-SentinelConfig,Test-SentinelApi,Ensure-SentinelUp,Invoke-Sentinel,Sentinel-*,*-Sentinel*
