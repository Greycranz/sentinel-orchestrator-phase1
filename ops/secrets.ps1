#!/usr/bin/env pwsh
# Cross-version PowerShell compatibility: works on 5.1 and 7+

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("set", "rotate", "test", "list")]
    [string]$Action,
    
    [Parameter(Position=1)]
    [ValidateSet("groq", "openai", "anthropic", "GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY")]
    [string]$Provider,
    
    [Parameter(Position=2)]
    [string]$Value
)

$ErrorActionPreference = "Stop"

# If running PS < 7, try to find and re-invoke with pwsh
if ($PSVersionTable.PSVersion.Major -lt 7) {
    $pwshPaths = @(
        "$env:ProgramFiles\PowerShell\7\pwsh.exe",
        "$env:ProgramFiles\PowerShell\6\pwsh.exe",
        (Get-Command pwsh -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
    ) | Where-Object { $_ -and (Test-Path $_) }
    
    if ($pwshPaths) {
        $pwsh = $pwshPaths[0]
        Write-Host "Re-invoking with PowerShell 7+ at: $pwsh"
        
        # Build argument list from bound parameters
        $argList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$PSCommandPath`"")
        
        foreach ($param in $PSBoundParameters.GetEnumerator()) {
            if ($param.Value) {
                if ($param.Key -eq "Action") {
                    $argList += "`"$($param.Value)`""
                } elseif ($param.Key -eq "Provider" -and $param.Value) {
                    $argList += "`"$($param.Value)`""
                } elseif ($param.Key -eq "Value" -and $param.Value) {
                    $argList += "`"$($param.Value)`""
                }
            }
        }
        
        Start-Process -FilePath $pwsh -ArgumentList $argList -Wait -NoNewWindow
        exit $LASTEXITCODE
    }
    # Fall back to PS 5.1 - continue execution
}

# Navigate to repo root
Set-Location (Split-Path $PSScriptRoot -Parent)

# Import .env.local if present
$envLocal = ".env.local"
if (Test-Path $envLocal) {
    Get-Content $envLocal | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Find Python executable
$pythonExe = "python"
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonExe = ".venv\Scripts\python.exe"
} elseif (Test-Path "venv\Scripts\python.exe") {
    $pythonExe = "venv\Scripts\python.exe"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonExe = "python3"
}

switch ($Action) {
    "set" {
        if (-not $Provider -or -not $Value) {
            Write-Error "Usage: .\ops\secrets.ps1 set <provider> <api_key>"
            exit 1
        }
        
        # Normalize provider name
        $normalizedProvider = $Provider -replace "_API_KEY", ""
        $normalizedProvider = $normalizedProvider.ToLower()
        
        $pythonScript = @"
from sentinel_engine.secrets.manager import secrets_manager
try:
    secrets_manager.set_key('$normalizedProvider', '$Value')
    print('✅ Set key for $normalizedProvider')
except Exception as e:
    print('❌ Error: {0}'.format(e))
    exit(1)
"@
        
        & $pythonExe -c $pythonScript
    }
    
    "rotate" {
        if (-not $Provider) {
            Write-Error "Usage: .\ops\secrets.ps1 rotate <provider>"
            exit 1
        }
        
        $normalizedProvider = $Provider -replace "_API_KEY", ""
        $normalizedProvider = $normalizedProvider.ToLower()
        
        # PS 5.1 compatible secure input
        $newKey = Read-Host -Prompt "Enter new API key for $normalizedProvider" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($newKey)
        $plainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
        
        $pythonScript = @"
from sentinel_engine.secrets.manager import secrets_manager
try:
    secrets_manager.rotate_key('$normalizedProvider', '$plainKey')
    print('✅ Rotated key for $normalizedProvider')
except Exception as e:
    print('❌ Error: {0}'.format(e))
    exit(1)
"@
        
        & $pythonExe -c $pythonScript
    }
    
    "test" {
        $pythonScript = @"
from sentinel_engine.secrets.manager import secrets_manager
import yaml
from pathlib import Path

def test_keys():
    policy_file = Path('ops/policy/keys.yml')
    if not policy_file.exists():
        print('❌ Policy file missing: ops/policy/keys.yml')
        return False
        
    with open(policy_file) as f:
        policy = yaml.safe_load(f)
    
    providers = policy.get('providers', {})
    success = True
    
    for provider in ['groq', 'openai', 'anthropic']:
        has_key = secrets_manager.has_valid_key(provider)
        status = '✅ Valid key' if has_key else '❌ No valid key'
        print('{0}: {1}'.format(provider, status))
        
        if not has_key:
            success = False
    
    return success

result = test_keys()
exit(0 if result else 1)
"@
        
        & $pythonExe -c $pythonScript
    }
    
    "list" {
        $pythonScript = @"
from sentinel_engine.secrets.manager import secrets_manager

providers = ['groq', 'openai', 'anthropic']
print('Provider Key Status:')
for provider in providers:
    has_key = secrets_manager.has_valid_key(provider)
    status = '✅ Present' if has_key else '❌ Missing'
    print('  {0:10} {1}'.format(provider, status))
"@
        
        & $pythonExe -c $pythonScript
    }
}
