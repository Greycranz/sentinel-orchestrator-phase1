# 🔄 SENTINEL SERVICE MANAGEMENT
# Start/stop/restart the Sentinel Engine service

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "install")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$ServiceName = "SentinelOrchestrator"
$RepoRoot = Get-Location

function Install-Service {
    Write-Host "🔧 Installing Sentinel Engine as Windows Service..." -ForegroundColor Yellow
    
    $VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
    
    if (-not (Test-Path $VenvPython)) {
        throw "Python venv not found. Run the main installer first."
    }
    
    # Check if NSSM is available
    $NssmPath = "C:\nssm\nssm.exe"
    if (-not (Test-Path $NssmPath)) {
        Write-Host "NSSM not found. Installing via PowerShell alternative..." -ForegroundColor Gray
        
        # Create scheduled task as service alternative
        $TaskName = "SentinelOrchestrator"
        $TaskAction = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-NoProfile -WindowStyle Hidden -Command `"cd '$RepoRoot'; & '$VenvPython' -m uvicorn sentinel_engine.api:app --host 127.0.0.1 --port 8001`""
        $TaskTrigger = New-ScheduledTaskTrigger -AtStartup
        $TaskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
        $TaskPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        Register-ScheduledTask -TaskName $TaskName -Action $TaskAction -Trigger $TaskTrigger -Settings $TaskSettings -Principal $TaskPrincipal -Force | Out-Null
        Start-ScheduledTask -TaskName $TaskName
        
        Write-Host "✅ Scheduled Task service installed and started" -ForegroundColor Green
        return
    }
    
    # Use NSSM if available
    try {
        & $NssmPath stop $ServiceName 2>$null | Out-Null
        & $NssmPath remove $ServiceName confirm 2>$null | Out-Null
    } catch {}
    
    & $NssmPath install $ServiceName $VenvPython
    & $NssmPath set $ServiceName AppParameters "-m uvicorn sentinel_engine.api:app --host 127.0.0.1 --port 8001 --log-level info"
    & $NssmPath set $ServiceName AppDirectory $RepoRoot
    & $NssmPath set $ServiceName DisplayName "Sentinel Engine Phase 2"
    & $NssmPath set $ServiceName Description "Sentinel Engine Multi-LLM Revenue Platform"
    & $NssmPath set $ServiceName Start SERVICE_AUTO_START
    & $NssmPath set $ServiceName AppStdout (Join-Path $RepoRoot "ops\logs\service.out.log")
    & $NssmPath set $ServiceName AppStderr (Join-Path $RepoRoot "ops\logs\service.err.log")
    & $NssmPath set $ServiceName AppRotateFiles 1
    & $NssmPath set $ServiceName AppRotateOnline 1
    & $NssmPath set $ServiceName AppRotateSeconds 86400
    
    & $NssmPath start $ServiceName
    Write-Host "✅ NSSM service installed and started" -ForegroundColor Green
}

function Get-ServiceStatus {
    # Check Windows Service
    $service = Get-Service $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "🔍 Windows Service Status:" -ForegroundColor Cyan
        Write-Host "   Name: $($service.Name)" -ForegroundColor Gray
        Write-Host "   Status: $($service.Status)" -ForegroundColor Gray
        Write-Host "   Start Type: $($service.StartType)" -ForegroundColor Gray
    }
    
    # Check Scheduled Task
    $task = Get-ScheduledTask "SentinelOrchestrator" -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "📅 Scheduled Task Status:" -ForegroundColor Cyan
        Write-Host "   Name: $($task.TaskName)" -ForegroundColor Gray
        Write-Host "   State: $($task.State)" -ForegroundColor Gray
        Write-Host "   Last Run: $($task.LastRunTime)" -ForegroundColor Gray
    }
    
    # Check if API is responding
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:8001/healthz" -TimeoutSec 3
        Write-Host "🌐 API Status:" -ForegroundColor Cyan
        Write-Host "   Endpoint: http://127.0.0.1:8001" -ForegroundColor Gray
        Write-Host "   Status: $($health.status)" -ForegroundColor Green
        Write-Host "   Service: $($health.service)" -ForegroundColor Gray
    } catch {
        Write-Host "🌐 API Status:" -ForegroundColor Cyan
        Write-Host "   Endpoint: http://127.0.0.1:8001" -ForegroundColor Gray
        Write-Host "   Status: Not responding" -ForegroundColor Red
    }
}

switch ($Action) {
    "install" {
        Install-Service
    }
    "start" {
        $service = Get-Service $ServiceName -ErrorAction SilentlyContinue
        if ($service) {
            Start-Service $ServiceName
            Write-Host "✅ Service started" -ForegroundColor Green
        } else {
            $task = Get-ScheduledTask "SentinelOrchestrator" -ErrorAction SilentlyContinue
            if ($task) {
                Start-ScheduledTask "SentinelOrchestrator"
                Write-Host "✅ Scheduled task started" -ForegroundColor Green
            } else {
                Write-Host "❌ No service or task found. Run with -Action install first" -ForegroundColor Red
            }
        }
    }
    "stop" {
        $service = Get-Service $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq "Running") {
            Stop-Service $ServiceName
            Write-Host "✅ Service stopped" -ForegroundColor Green
        }
        
        $task = Get-ScheduledTask "SentinelOrchestrator" -ErrorAction SilentlyContinue
        if ($task) {
            Stop-ScheduledTask "SentinelOrchestrator" -ErrorAction SilentlyContinue
            Write-Host "✅ Scheduled task stopped" -ForegroundColor Green
        }
    }
    "restart" {
        & $MyInvocation.MyCommand.Path -Action stop
        Start-Sleep 2
        & $MyInvocation.MyCommand.Path -Action start
    }
    "status" {
        Get-ServiceStatus
    }
}
