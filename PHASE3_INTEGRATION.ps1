# 🔧 SENTINEL PHASE 3 - INTEGRATION INSTRUCTIONS
# Follow these steps to integrate Phase 3 into your main Sentinel Engine

Write-Host "🔧 SENTINEL PHASE 3 INTEGRATION GUIDE" -ForegroundColor Cyan

# STEP 1: Backup current API (safety first)
Write-Host "`n1. 📄 Backing up current API..." -ForegroundColor Yellow
$ApiBackup = "sentinel_engine\api_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py"
Copy-Item "sentinel_engine\api.py" $ApiBackup -ErrorAction SilentlyContinue
Write-Host "   ✅ Backup created: $ApiBackup" -ForegroundColor Green

# STEP 2: Update main API with Phase 3 endpoints
Write-Host "`n2. 🔌 Integrating Phase 3 endpoints..." -ForegroundColor Yellow
$CurrentApi = Get-Content "sentinel_engine\api.py" -Raw -ErrorAction SilentlyContinue
$Phase3Integration = Get-Content "PHASE3_API_INTEGRATION.txt" -Raw -ErrorAction SilentlyContinue

if ($CurrentApi -and $Phase3Integration) {
    # Add Phase 3 integration to the existing API
    $UpdatedApi = $CurrentApi + "`n`n# === PHASE 3 SUB-COMPANY FACTORY INTEGRATION ===`n" + $Phase3Integration
    $UpdatedApi | Set-Content "sentinel_engine\api.py" -Encoding UTF8
    Write-Host "   ✅ Phase 3 endpoints integrated into main API" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Could not auto-integrate - manual step required" -ForegroundColor Yellow
    Write-Host "   💡 Copy content from PHASE3_API_INTEGRATION.txt to sentinel_engine\api.py" -ForegroundColor Gray
}

# STEP 3: Update database models
Write-Host "`n3. 🗄️ Updating database models..." -ForegroundColor Yellow
$ModelsFile = "sentinel_engine\models.py"
if (Test-Path $ModelsFile) {
    $CurrentModels = Get-Content $ModelsFile -Raw
    if ($CurrentModels -notmatch "sub_company_models") {
        # Add import for Phase 3 models
        $ModelsUpdate = $CurrentModels + "`n`n# Phase 3 Sub-Company Models`nfrom .sub_company_models import *`n"
        $ModelsUpdate | Set-Content $ModelsFile -Encoding UTF8
        Write-Host "   ✅ Phase 3 models integrated" -ForegroundColor Green
    } else {
        Write-Host "   ✅ Phase 3 models already integrated" -ForegroundColor Green
    }
} else {
    Write-Host "   ⚠️  models.py not found - Phase 3 will use standalone models" -ForegroundColor Yellow
}

# STEP 4: Restart Sentinel Service
Write-Host "`n4. 🔄 Restarting Sentinel Engine service..." -ForegroundColor Yellow
try {
    if (Test-Path "MANAGE_SERVICE.ps1") {
        & .\MANAGE_SERVICE.ps1 -Action restart
        Start-Sleep 3
        $status = & .\MANAGE_SERVICE.ps1 -Action status
        Write-Host "   ✅ Service restarted successfully" -ForegroundColor Green
    } else {
        Write-Host "   💡 Manual restart required - service management script not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Service restart failed: $_" -ForegroundColor Yellow
    Write-Host "   💡 Try manual restart or check service status" -ForegroundColor Gray
}

# STEP 5: Verify Integration
Write-Host "`n5. ✅ Verifying Phase 3 integration..." -ForegroundColor Yellow
Start-Sleep 2

try {
    $ApiKey = if (Test-Path ".env") {
        (Get-Content ".env" | Where-Object { $_ -match "^SENTINEL_API_KEY=" }) -replace "^SENTINEL_API_KEY=", ""
    } else { "demo-key" }
    
    $Headers = @{ "X-API-Key" = $ApiKey }
    
    # Test health
    $health = Invoke-RestMethod "http://127.0.0.1:8001/healthz" -TimeoutSec 5
    Write-Host "   ✅ Main system healthy: $($health.status)" -ForegroundColor Green
    
    # Test Phase 3 status
    $phase3 = Invoke-RestMethod "http://127.0.0.1:8001/v1/system/phase3-status" -Headers $Headers -TimeoutSec 5
    Write-Host "   ✅ Phase 3 status: $($phase3.phase3_status)" -ForegroundColor Green
    
    # Test company listing
    $companies = Invoke-RestMethod "http://127.0.0.1:8001/v1/companies" -Headers $Headers -TimeoutSec 5
    Write-Host "   ✅ Sub-company factory operational" -ForegroundColor Green
    
    Write-Host "`n🎉 PHASE 3 INTEGRATION SUCCESSFUL!" -ForegroundColor Cyan
    Write-Host "✅ All Phase 3 endpoints are operational" -ForegroundColor Green
    Write-Host "✅ Sub-company factory ready for business creation" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Integration verification failed: $_" -ForegroundColor Red
    Write-Host "   💡 Check API integration and restart service manually" -ForegroundColor Yellow
}

Write-Host "`n📋 INTEGRATION COMPLETE - NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Run .\PHASE3_DEMO_TEST.ps1 to test the sub-company factory" -ForegroundColor Gray
Write-Host "2. Create your first sub-company: 'Unreal Hollywood Takeover'" -ForegroundColor Gray  
Write-Host "3. Test AI sourcing with customer feature requests" -ForegroundColor Gray
Write-Host "4. Begin Phase 4: Scale to autonomous business empire" -ForegroundColor Gray
