# Start Issuer Server (College Backend)
Write-Host "Starting Issuer (College) Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python issuer/app.py"

# Wait a moment
Start-Sleep -Seconds 2

# Start Verifier Server (Scholarship Backend)
Write-Host "Starting Verifier (Scholarship) Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python verifier/app.py"

# Wait a moment
Start-Sleep -Seconds 2

# Open student portal in browser
Write-Host "Opening Student Portal..." -ForegroundColor Green
$studentPortal = Join-Path $PSScriptRoot "student\home.html"
Start-Process $studentPortal

Write-Host "`nAll services started!" -ForegroundColor Cyan
Write-Host "Issuer Server: http://localhost:5001" -ForegroundColor Yellow
Write-Host "Verifier Server: http://localhost:5002" -ForegroundColor Yellow
Write-Host "Home Page: Opened in browser" -ForegroundColor Yellow
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
