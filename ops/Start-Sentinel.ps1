param(
  [string]\System.Management.Automation.Internal.Host.InternalHost = "127.0.0.1",
  [int]\ = 8001
)
\Stop = "Stop"
Set-Location "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1"

# kill any old listener on this port
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  ? { \.CommandLine -match 'uvicorn.*' + [regex]::Escape(\System.Management.Automation.Internal.Host.InternalHost) + '.*' + [regex]::Escape(\.ToString()) } |
  % { Stop-Process -Id \.ProcessId -Force -ErrorAction SilentlyContinue }

\ = ".\.venv\Scripts\python.exe"
\   = "-m uvicorn sentinel_engine.api:app --host \System.Management.Automation.Internal.Host.InternalHost --port \ --log-level info"
\ = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1\ops\logs\uvicorn.out.log"
\ = "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1\ops\logs\uvicorn.err.log"

Start-Process -FilePath \ -ArgumentList \ -WindowStyle Hidden 
  -WorkingDirectory "C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1" 
  -RedirectStandardOutput \ -RedirectStandardError \
