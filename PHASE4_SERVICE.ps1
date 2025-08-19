param([string]$Action = "status")

function Start-Service {
    Write-Host "Starting Sentinel Engine..."
    $python = ".\.venv\Scripts\python.exe"
    
    if (-not (Test-Path $python)) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
        & $python -m pip install fastapi uvicorn
    }
    
    Start-Process -FilePath $python -ArgumentList @("-m", "uvicorn", "sentinel_engine.api:app", "--host", "127.0.0.1", "--port", "8001") -WindowStyle Hidden
    Start-Sleep 5
    
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:8001/healthz" -TimeoutSec 5
        Write-Host "SUCCESS: Sentinel Engine started"
        Write-Host "Web Console: http://127.0.0.1:8001"
        Write-Host "API Docs: http://127.0.0.1:8001/docs"
    } catch {
        Write-Host "ERROR: Failed to start service"
    }
}

function Stop-Service {
    Write-Host "Stopping Sentinel Engine..."
    Get-Process -Name "python" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -and $_.CommandLine.Contains("sentinel_engine") } |
        Stop-Process -Force
    Write-Host "Service stopped"
}

function Test-Service {
    Write-Host "Testing Sentinel Engine..."
    try {
        $test = Invoke-RestMethod "http://127.0.0.1:8001/api/system/test" -TimeoutSec 5
        Write-Host "Test Result: $($test.status)"
        Write-Host "Components: $($test.components_loaded)"
        Write-Host "Emergency Controls: $($test.emergency_controls)"
    } catch {
        Write-Host "ERROR: Service not responding"
    }
}

switch ($Action) {
    "start" { Start-Service }
    "stop" { Stop-Service }
    "restart" { Stop-Service; Start-Sleep 2; Start-Service }
    "test" { Test-Service }
    "status" {
        try {
            $health = Invoke-RestMethod "http://127.0.0.1:8001/healthz" -TimeoutSec 3
            Write-Host "STATUS: RUNNING - $($health.status)"
        } catch {
            Write-Host "STATUS: NOT RUNNING"
        }
    }
}
