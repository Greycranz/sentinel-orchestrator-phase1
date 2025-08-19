# SENTINEL SERVICE MANAGER
param([Parameter(Mandatory)][ValidateSet("start", "stop", "restart", "status")][string]$Action)

$RepoRoot = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1"
$PythonExe = "$RepoRoot\.venv\Scripts\python.exe"

switch ($Action) {
    "start" {
        Write-Host "🚀 Starting Sentinel Engine..." -ForegroundColor Green
        Set-Location $RepoRoot
        Start-Process $PythonExe -ArgumentList "-m", "uvicorn", "sentinel_engine.api:app", "--host", "127.0.0.1", "--port", "8001", "--log-level", "info" -WindowStyle Hidden
        Start-Sleep 3
        try {
            $health = Invoke-RestMethod "http://127.0.0.1:8001/healthz"
            Write-Host "✅ Service started: $($health.status)" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ Service may still be starting..." -ForegroundColor Yellow
        }
    }
    "stop" {
        Write-Host "⏹️ Stopping Sentinel Engine..." -ForegroundColor Yellow
        Get-Process | Where-Object {$_.ProcessName -like '*python*' -and $_.CommandLine -like '*uvicorn*'} | Stop-Process -Force
        Write-Host "✅ Service stopped" -ForegroundColor Green
    }
    "restart" {
        & "$PSCommandPath" -Action stop
        Start-Sleep 2
        & "$PSCommandPath" -Action start
    }
    "status" {
        try {
            $health = Invoke-RestMethod "http://127.0.0.1:8001/healthz" -TimeoutSec 5
            Write-Host "Status: RUNNING ($($health.status))" -ForegroundColor Green
        } catch {
            Write-Host "Status: STOPPED" -ForegroundColor Red
        }
    }
}
