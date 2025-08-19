# Sentinel Engine — Cross-device sync

This repo is designed to work seamlessly across Windows (Alienware) and macOS, with a single GitHub remote.

## Windows → first-time push
1) Ensure Git and (optionally) GitHub CLI are installed and authenticated.
2) Run: .\ops\git-setup.ps1

## macOS → first-time clone
Run ops/git-setup.sh (after Windows creates the remote) or:
git clone https://github.com/<owner>/sentinel-orchestrator-phase1.git ~/sentinel-company/sentinel-orchestrator-phase1

## Daily workflow (Windows PowerShell)
Set-Location 'C:\Users\mdee2\sentinel-company\sentinel-orchestrator-phase1'
git pull --rebase
# make changes...
git add -A
git commit -m "Describe change"
git push

## Daily workflow (macOS bash/zsh)
cd ~/sentinel-company/sentinel-orchestrator-phase1
git pull --rebase
# make changes...
git add -A && git commit -m "Describe change" && git push

## Secrets (never commit)
Windows:
  .\ops\secrets.ps1 list
  .\ops\secrets.ps1 set groq <REDACTED>

macOS:
  ./ops/secrets.sh list
  ./ops/secrets.sh set groq <REDACTED>
