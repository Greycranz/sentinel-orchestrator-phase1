# 🆓 FREE API KEYS SETUP GUIDE
# Copy each URL to get your free API keys

Write-Host "=== FREE API KEYS - GET THESE NOW ===" -ForegroundColor Cyan
Write-Host "Phase 2 needs these free keys for customer demos:" -ForegroundColor Yellow

Write-Host "`n1. 🚀 GROQ (Completely FREE - GET THIS FIRST):" -ForegroundColor Green
Write-Host "   https://console.groq.com/keys" -ForegroundColor Gray
Write-Host "   - Sign up with Google/GitHub (30 seconds)" -ForegroundColor Gray
Write-Host "   - Get API key instantly" -ForegroundColor Gray
Write-Host "   - Fast inference, no credit card needed" -ForegroundColor Gray

Write-Host "`n2. 🧠 GOOGLE GEMINI (Free tier - 15 RPM):" -ForegroundColor Green
Write-Host "   https://aistudio.google.com/app/apikey" -ForegroundColor Gray
Write-Host "   - Sign up with Google account" -ForegroundColor Gray
Write-Host "   - Great for analysis tasks" -ForegroundColor Gray

Write-Host "`n3. 🤗 HUGGING FACE (100% free models):" -ForegroundColor Green
Write-Host "   https://huggingface.co/settings/tokens" -ForegroundColor Gray
Write-Host "   - Create account and access token" -ForegroundColor Gray
Write-Host "   - Access all open source models" -ForegroundColor Gray

Write-Host "`n4. 🔥 OPENAI (Optional - $5 free credit):" -ForegroundColor Green
Write-Host "   https://platform.openai.com/api-keys" -ForegroundColor Gray
Write-Host "   - Use for high-value customer demos" -ForegroundColor Gray

Write-Host "`nAfter getting keys, update .env file:" -ForegroundColor Cyan
Write-Host "Edit .env and replace 'your_*_key_here' with actual keys" -ForegroundColor Gray

Write-Host "`nAUTO-EDIT .env FILE:" -ForegroundColor Yellow
Write-Host "Run these commands with your actual keys:" -ForegroundColor Gray
Write-Host "(Get-Content .env) -replace 'your_groq_key_here', 'YOUR_ACTUAL_GROQ_KEY' | Set-Content .env" -ForegroundColor Gray
Write-Host "(Get-Content .env) -replace 'your_google_key_here', 'YOUR_ACTUAL_GOOGLE_KEY' | Set-Content .env" -ForegroundColor Gray
