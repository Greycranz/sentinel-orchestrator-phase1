$RepoRoot = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1"
$ServePS1 = Join-Path $RepoRoot "ops\scripts\serve.ps1"
$Host = "127.0.0.1"; $Port = 8001

$alive = Get-NetTCPConnection -LocalAddress $Host -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $alive) {
  Start-Process -WindowStyle Hidden -FilePath "pwsh.exe" -ArgumentList @("-NoProfile","-File",$ServePS1) | Out-Null
}
