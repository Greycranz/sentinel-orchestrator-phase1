# Sentinel Engine PowerShell Admin Module

$script:ApiKey = "ytOTqqiZ9jvpW3yPruv4ryM297uszGC1V6+/mpt7Odo="
$script:BaseUrl = "http://127.0.0.1:8001"

function Get-SentinelStatus {
    try {
        $response = Invoke-RestMethod "$script:BaseUrl/healthz" -TimeoutSec 5
        Write-Host "Sentinel Status: " -NoNewline
        Write-Host "$($response.status)" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "Sentinel Status: " -NoNewline  
        Write-Host "DOWN" -ForegroundColor Red
        return $null
    }
}

function Get-SentinelMetrics {
    $headers = @{ "X-API-Key" = $script:ApiKey }
    try {
        Invoke-RestMethod "$script:BaseUrl/metrics" -Headers $headers
    } catch {
        Write-Error "Failed to get metrics: $_"
    }
}

function Add-SentinelJob {
    param(
        [string]$Kind = "echo",
        [hashtable]$Payload = @{message="test"}
    )
    $headers = @{ "X-API-Key" = $script:ApiKey }
    $body = @{ kind = $Kind; payload = $Payload } | ConvertTo-Json
    try {
        Invoke-RestMethod "$script:BaseUrl/v0/jobs/enqueue" -Method POST -Headers $headers -Body $body -ContentType "application/json"
    } catch {
        Write-Error "Failed to enqueue job: $_"
    }
}

function Get-SentinelJobTotals {
    $headers = @{ "X-API-Key" = $script:ApiKey }
    try {
        Invoke-RestMethod "$script:BaseUrl/v0/jobs/totals" -Headers $headers
    } catch {
        Write-Error "Failed to get job totals: $_"
    }
}

function Get-SentinelLogs {
    param([int]$Tail = 50)
    $LogPath = 'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1\ops\logs\service.out.log'
    if (Test-Path $LogPath) {
        Get-Content $LogPath -Tail $Tail
    } else {
        Write-Warning "Log file not found: $LogPath"
    }
}

function Restart-SentinelService {
    Restart-Service 'SentinelOrchestrator'
    Start-Sleep 3
    Get-SentinelStatus
}

function Get-SentinelApiKey {
    return $script:ApiKey
}

function Show-SentinelInfo {
    Write-Host "=== Sentinel Engine Info ===" -ForegroundColor Cyan
    Write-Host "API URL: $script:BaseUrl" -ForegroundColor White
    Write-Host "API Key: $script:ApiKey" -ForegroundColor Yellow
    Write-Host "Service: SentinelOrchestrator" -ForegroundColor White
    Write-Host "Repository: C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1" -ForegroundColor White
    Write-Host ""
    Write-Host "Available Commands:" -ForegroundColor Green
    Write-Host "  Get-SentinelStatus" -ForegroundColor Gray
    Write-Host "  Get-SentinelMetrics" -ForegroundColor Gray
    Write-Host "  Add-SentinelJob -Kind echo -Payload @{message='Hello'}" -ForegroundColor Gray
    Write-Host "  Get-SentinelJobTotals" -ForegroundColor Gray
    Write-Host "  Get-SentinelLogs" -ForegroundColor Gray
    Write-Host "  Restart-SentinelService" -ForegroundColor Gray
}

# Auto-show info when module loads
Show-SentinelInfo

Export-ModuleMember -Function Get-SentinelStatus, Get-SentinelMetrics, Add-SentinelJob, Get-SentinelJobTotals, Get-SentinelLogs, Restart-SentinelService, Get-SentinelApiKey, Show-SentinelInfo
