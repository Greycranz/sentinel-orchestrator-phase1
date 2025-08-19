# ops\scripts\run-agent.ps1  (ROBUST v0 client)
param(
  [string]$Base   = "http://127.0.0.1:8001",
  [string]$LogDir = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1\ops\logs"
)
$ErrorActionPreference = "Stop"

# --- logging ---
$null  = New-Item -ItemType Directory -Force -Path $LogDir
$stamp = (Get-Date -Format 'yyyyMMdd-HHmmss')
$log   = Join-Path $LogDir "agent-$stamp.log"
function Log([string]$m){ "$(Get-Date -Format s) [agent] $m" | Tee-Object -FilePath $log -Append | Out-Null }

# --- config: get API key from env or .env fallback ---
$ApiKey = $env:SENTINEL_API_KEY
if (-not $ApiKey) {
  $envPath = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1\.env"
  if (Test-Path $envPath) {
    $ApiKey = (Get-Content $envPath | ? { $_ -match '^SENTINEL_API_KEY=' } | Select-Object -Last 1) -replace '^SENTINEL_API_KEY=',''
  }
}
if (-not $ApiKey) { Log "SENTINEL_API_KEY missing (env & .env)"; exit 2 }
$Hdr    = @{ "X-API-Key" = $ApiKey }
$BaseV0 = "$Base/v0"

# --- helpers ---
function Wait-ApiReady([string]$BaseUrl,[int]$TimeoutSec=60){
  $stop=(Get-Date).AddSeconds($TimeoutSec)
  do { try{ if((Invoke-RestMethod "$BaseUrl/healthz" -TimeoutSec 2).status -eq 'ok'){ return $true } }catch{}; Start-Sleep -Milliseconds 600 } while((Get-Date) -lt $stop)
  return $false
}
function JGET([string]$u){ Invoke-RestMethod -Uri $u -Headers $Hdr -Method GET -TimeoutSec 30 }
function JPOST([string]$u,[object]$b){ Invoke-RestMethod -Uri $u -Headers $Hdr -Method POST -ContentType "application/json" -Body (ConvertTo-Json $b -Depth 12) -TimeoutSec 30 }

# --- wait for API ---
if (-not (Wait-ApiReady -BaseUrl $Base)) { Log "API not ready"; exit 5 }

# --- register (tenant must be a string) ---
$host = $env:COMPUTERNAME
try { $reg = JPOST "$BaseV0/agents/register" @{ name="dev-agent-$host"; host=$host; tenant="1" } }
catch { Log "register failed: $($_.Exception.Message)"; exit 6 }

# pick id from any field
$agentId=$null
foreach($k in 'id','agent_id','uid','guid','agentId','AgentId'){ if($reg.PSObject.Properties.Name -contains $k){ $agentId=[string]$reg.$k; if($agentId){ break } } }
if (-not $agentId){ Log ("register returned no id; raw="+($reg|ConvertTo-Json -Compress)); exit 7 }
Log "registered agent id=$agentId"

# --- allowlisted handlers ---
function Handle([hashtable]$job){
  $kind=[string]$job.kind
  $pl=@{}; if($job.payload_json){ try{ $pl=($job.payload_json|ConvertFrom-Json -Depth 12) }catch{ $pl=@{} } }
  switch($kind){
    'echo'             { return @{ ok=$true; echo=([string]($pl.msg ?? "")); at=(Get-Date).ToString('o') } }
    'ps:get-date'      { return @{ now=(Get-Date).ToString('o') } }
    'ps:get-process'   {
      $n=[string]($pl.name ?? ""); if($n -and $n -notmatch '^[A-Za-z0-9_.:-]{1,64}$'){ throw "bad token 'name'" }
      return (if($n){ Get-Process -Name $n -ErrorAction SilentlyContinue } else { Get-Process }) | Select-Object Name,Id,CPU,WS,StartTime -ErrorAction SilentlyContinue
    }
    'ps:get-service'   {
      $n=[string]($pl.name ?? ""); if($n -and $n -notmatch '^[A-Za-z0-9_.:-]{1,64}$'){ throw "bad token 'name'" }
      return (if($n){ Get-Service -Name $n -ErrorAction SilentlyContinue } else { Get-Service }) | Select-Object Name,Status,DisplayName
    }
    'ps:listdir'       {
      $p=[string]($pl.path ?? "C:\Windows"); if(-not (Test-Path $p)){ throw "path not found" }
      return Get-ChildItem -LiteralPath $p -Force | Select-Object Mode,Length,Name,FullName,LastWriteTime
    }
    default            { throw "unknown kind: $kind" }
  }
}

# --- main loop ---
while($true){
  try{
    # heartbeat (send both id & agent_id)
    try { JPOST "$BaseV0/agents/heartbeat" @{ id=$agentId; agent_id=$agentId; at=(Get-Date).ToUniversalTime().ToString('s') } | Out-Null }
    catch { Log "heartbeat failed: $($_.Exception.Message)" }

    # claim
    $cl=$null; try{ $cl=JGET "$BaseV0/jobs/claim?agent_id=$agentId" }catch{ Log "claim failed: $($_.Exception.Message)" }
    if($cl -and $cl.id){
      Log "claimed job id=$($cl.id) kind=$($cl.kind)"
      try{
        $out=Handle $cl
        JPOST "$BaseV0/jobs/$($cl.id)/complete" @{ status="completed"; output_json=($out | ConvertTo-Json -Depth 12) } | Out-Null
        Log "job #$($cl.id) completed"
      }catch{
        JPOST "$BaseV0/jobs/$($cl.id)/complete" @{ status="failed"; output_json=(@{ ok=$false; error=$_.Exception.Message }|ConvertTo-Json -Depth 8) } | Out-Null
        Log "job #$($cl.id) FAILED: $($_.Exception.Message)"
      }
    }
  }catch{ Log "loop error: $($_.Exception.Message)" }
  Start-Sleep -Seconds 3
}
