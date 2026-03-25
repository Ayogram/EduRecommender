# EduRecommender Auto-Setup Script (Windows)
# --------------------------------------------------

Clear-Host
Write-Host "🚀 Welcome to EduRecommender Auto-Setup Assistant" -ForegroundColor Cyan
Write-Host "--------------------------------------------------" -ForegroundColor Cyan

# 1. Detect Python
$pythonPath = "C:\Users\USER\AppData\Local\Programs\Python\Python312\python.exe"
if (!(Test-Path $pythonPath)) {
    Write-Host "⚠️ Python 3.12 not found at default path. Searching..." -ForegroundColor Yellow
    $pythonPath = where.exe python | Select-Object -First 1
}

if (!$pythonPath) {
    Write-Host "❌ Python is not installed. Please install Python 3.12 from python.org" -ForegroundColor Red
    exit
}

Write-Host "✅ Found Python: $pythonPath" -ForegroundColor Green

# 2. Create Virtual Environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor White
& $pythonPath -m venv venv
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Failed to create venv" -ForegroundColor Red; exit }

# 3. Install Dependencies
Write-Host "📥 Installing all dependencies (this may take a minute)..." -ForegroundColor White
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "❌ Failed to install dependencies" -ForegroundColor Red; exit }

# 4. Setup Admin Account
Write-Host "`n🔐 SECURITY SETUP" -ForegroundColor Cyan
$adminEmail = Read-Host "Enter your Admin Gmail address"
$adminPassword = Read-Host "Create an Admin Password (or leave blank for 'Admin@123')"
if (!$adminPassword) { $adminPassword = "Admin@123" }

# 5. Initialize Database
Write-Host "`n🗄️ Initializing database and seeding data..." -ForegroundColor White
& .\venv\Scripts\python.exe seed_data.py "$adminEmail" "$adminPassword"

# 6. Success
Write-Host "`n✨ SETUP COMPLETE! ✨" -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Green
Write-Host "To run the application:" -ForegroundColor White
Write-Host "1. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "2. Run app:      python app.py" -ForegroundColor Yellow
Write-Host "--------------------------------------------------" -ForegroundColor Green
Write-Host "Admin Login: $adminEmail / $adminPassword" -ForegroundColor White
Write-Host "URL: http://127.0.0.1:5000" -ForegroundColor White
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
