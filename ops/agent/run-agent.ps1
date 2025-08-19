param([string]$AgentPath)
$stamp=Get-Date -Format "yyyyMMdd-HHmmss"
$log  =Join-Path (Split-Path -Parent $AgentPath) "..\logs\agent-$stamp.log"
"$stamp starting sentinel agent" | Tee-Object -FilePath $log
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File $AgentPath 2>&1 | Tee-Object -FilePath $log -Append
