param(
  [string]$Base = "http://127.0.0.1:8001/v0",
  [string]$Tenant = "1",
  [int]$HeartbeatSeconds = 25,
  [int]$PollSeconds = 2
)

$ErrorActionPreference = "Continue"

function Mask($s) {
  if (-not $s) { return "" }
  if ($s.Length -le 6) { return ("*" * $s.Length) }
  return ($s.Substring(0,3) + ("*" * [Math]::Max(0, $s.Length-6)) + $s.Substring($s.Length-3))
}

# simple token validator: only letters/digits/_ . -, and length cap
function Test-SimpleToken([string]$s, [int]$maxLen=64) {
  if (-not $s) { return $false }
  if ($s.Length -gt $maxLen) { return $false }
  return -not ($s -match '[^\w\.\-]')
}

# Compute repo root from this script's folder
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$EnvPath  = Join-Path $RepoRoot ".env"

# Resolve API key
$EnvKey = [Environment]::GetEnvironmentVariable("SENTINEL_API_KEY")
$KeySource = "process env"
if (-not $EnvKey -or -not $EnvKey.Trim()) {
  $m = Select-String -Path $EnvPath -Pattern '^\s*SENTINEL_API_KEY\s*=\s*(.+?)\s*$' -ErrorAction SilentlyContinue
  if ($m) { $EnvKey = $m.Matches[0].Groups[1].Value; $KeySource = ".env" }
}
$EnvKey = ($EnvKey | ForEach-Object { $_ })
if (-not $EnvKey -or -not $EnvKey.Trim()) {
  "FATAL: Missing SENTINEL_API_KEY (env or $EnvPath)" | Write-Host
  exit 1
}
$EnvKey = $EnvKey.Trim()
"agent: using API key from ${KeySource}: $(Mask($EnvKey))" | Write-Host
$Hdr = @{ "X-API-Key" = $EnvKey }

function Invoke-JsonPost($url, $body) {
  try {
    return Invoke-RestMethod -Uri $url -Method POST -Headers $Hdr -Body ($body | ConvertTo-Json -Depth 12) -ContentType "application/json" -TimeoutSec 15
  } catch {
    "POST $url failed: $($_.Exception.Message)" | Write-Host
    if ($_.Exception.Response -and $_.Exception.Response.GetResponseStream) {
      try { $sr = New-Object IO.StreamReader($_.Exception.Response.GetResponseStream()); "POST body: " + $sr.ReadToEnd() | Write-Host } catch {}
    }
    throw
  }
}

function Try-JsonGet($url, $qs) {
  $q = ""
  if ($qs) {
    $pairs = @()
    foreach ($k in $qs.Keys) {
      if ($null -ne $k) {
        $val = $qs[$k]
        $pairs += ("{0}={1}" -f [uri]::EscapeDataString([string]$k), [uri]::EscapeDataString([string]$val))
      }
    }
    if ($pairs.Count -gt 0) { $q = "?" + ($pairs -join "&") }
  }
  try { return Invoke-RestMethod -Uri ($url + $q) -Method GET -Headers $Hdr -TimeoutSec 15 } catch { return $null }
}

"$(Get-Date -Format yyyyMMdd-HHmmss) starting sentinel agent" | Write-Host

# Register with retries
$regBody = @{ tenant=$Tenant; name="$($env:COMPUTERNAME)-agent"; platform="windows" }
$agentId = $null
$attempt = 0
while (-not $agentId) {
  $attempt++
  try {
    $resp = Invoke-JsonPost "$Base/agents/register" $regBody
    $agentId = $resp.agent_id
    if (-not $agentId) { throw "No agent_id in response" }
    "agent_id: $agentId (registered on attempt $attempt)" | Write-Host
  } catch {
    "REGISTRATION FAILED (attempt $attempt): $($_.Exception.Message)" | Write-Host
    Start-Sleep -Seconds ([Math]::Min(15, 2 * $attempt))
  }
}
$nextHb = Get-Date

# Main loop
while ($true) {
  $now = Get-Date
  if ($now -ge $nextHb) {
    try { Invoke-JsonPost "$Base/agents/heartbeat" @{ agent_id=$agentId; status="idle"; metrics=@{} } | Out-Null } catch {}
    $nextHb = $now.AddSeconds($HeartbeatSeconds)
  }

  $claim = Try-JsonGet "$Base/agents/jobs" @{ agent_id=$agentId; tenant=$Tenant }
  if ($null -ne $claim -and $claim.job -and $claim.job.id) {
    $j = $claim.job
    $status="failed"; $out=$null; $err=$null; $logs=@()
    switch ($j.type) {
      "echo" {
        $msg=$j.payload.msg
        $status="success"; $out=@{ echoed=$msg }; $logs=@("echoed: $msg")
      }
      "ps" {
        # Allowed commands with guarded params
        $allowed = @("Get-Date","Get-Process","Get-Service","Get-ChildItem")
        $cmd = [string]$j.payload.command
        if (-not $cmd -or -not ($allowed -contains $cmd)) {
          $status = "failed"; $err = "command not allowed"; $logs = @("blocked: $cmd")
        } else {
          try {
            switch ($cmd) {
              "Get-Date" { $data = Get-Date }
              "Get-Process" {
                $name = [string]$j.payload.name
                if ($name) {
                  if (-not (Test-SimpleToken $name 64)) { throw "invalid name" }
                  $data = Get-Process -Name $name -ErrorAction Stop
                } else { $data = Get-Process }
              }
              "Get-Service" {
                $name = [string]$j.payload.name
                if ($name) {
                  if (-not (Test-SimpleToken $name 128)) { throw "invalid name" }
                  $data = Get-Service -Name $name -ErrorAction Stop
                } else { $data = Get-Service }
              }
              "Get-ChildItem" {
                $path  = [string]$j.payload.path
                if (-not $path) { $path = "." }
                # basic path sanity (no wildcards)
                if ($path -match '[\*\?\|]') { throw "invalid path" }
                $depth = [int]($j.payload.depth)
                if ($depth -lt 0 -or $depth -gt 1) { $depth = 1 }
                $data = Get-ChildItem -Path $path -Depth $depth -ErrorAction Stop
              }
            }
            $status = "success"
            $out = @{ stdout = ($data | Out-String).Trim() }
            $logs = @("ran: $cmd")
          } catch {
            $status = "failed"; $err = $_.Exception.Message; $logs = @("error running: $cmd")
          }
        }
      }
      default { $err="unsupported job type: $($j.type)"; $logs=@("no-op") }
    }
    try {
      Invoke-JsonPost "$Base/agents/results" @{ agent_id=$agentId; job_id=$j.id; status=$status; output=$out; error=$err; logs=$logs } | Out-Null
      "handled job $($j.id): $status" | Write-Host
    } catch {
      "submit failed for job $($j.id): $($_.Exception.Message)" | Write-Host
    }
  }
  Start-Sleep -Seconds $PollSeconds
}

