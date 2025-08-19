param(
  [string]$HostAddress = "127.0.0.1",
  [int]$Port = 8001,
  [string]$LogLevel = "info"
)

$ErrorActionPreference = "Stop"
$RepoRoot = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1"
$VenvPy   = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$LogsDir  = Join-Path $RepoRoot "ops\logs"
$PidFile  = Join-Path $RepoRoot "ops\sentinel.pid"

New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
$EnvFile = Join-Path $RepoRoot ".env"
if (-not (Test-Path $EnvFile)) {
  "SENTINEL_API_KEY=super-secret-change-me" | Set-Content -Path $EnvFile -Encoding UTF8
}

# If already listening, exit quietly
$inUse = (Get-NetTCPConnection -LocalAddress $HostAddress -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
if ($inUse) { exit 0 }

$stdout = Join-Path $LogsDir "uvicorn.out.log"
$stderr = Join-Path $LogsDir "uvicorn.err.log"

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName  = $VenvPy
$psi.ArgumentList.Add("-m")
$psi.ArgumentList.Add("uvicorn")
$psi.ArgumentList.Add("sentinel_engine.api:app")
$psi.ArgumentList.Add("--host"); $psi.ArgumentList.Add($HostAddress)
$psi.ArgumentList.Add("--port"); $psi.ArgumentList.Add([string]$Port)
$psi.ArgumentList.Add("--log-level"); $psi.ArgumentList.Add($LogLevel)
$psi.WorkingDirectory     = $RepoRoot
$psi.RedirectStandardOut  = $true
$psi.RedirectStandardError= $true
$psi.UseShellExecute      = $false
$psi.CreateNoWindow       = $true

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi

$stdOutWriter = [System.IO.StreamWriter]::new($stdout, $true)
$stdErrWriter = [System.IO.StreamWriter]::new($stderr, $true)
$p.add_OutputDataReceived({ param($s,$e) if ($e.Data) { $stdOutWriter.WriteLine($e.Data); $stdOutWriter.Flush() } })
$p.add_ErrorDataReceived( { param($s,$e) if ($e.Data) { $stdErrWriter.WriteLine($e.Data); $stdErrWriter.Flush() } })

$p.Start() | Out-Null
$p.BeginOutputReadLine()
$p.BeginErrorReadLine()
$p.Id | Out-File -FilePath $PidFile -Encoding ascii -Force
exit 0
