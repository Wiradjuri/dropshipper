# Vercel Preflight Script for Dropshipper
param()

Write-Host "== Dropshipper Vercel Preflight =="

# Check Node version
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) { Write-Error 'Node.js not found'; exit 1 }
if ($nodeVersion -notmatch '^v20\\.') { Write-Error "Node 20.x required, found $nodeVersion"; exit 1 }
Write-Host "Node version: $nodeVersion"

# Check Python version
$pythonVersion = python --version 2>&1
if ($pythonVersion -notmatch '3\\.1[2-9]') { Write-Error "Python 3.12+ required, found $pythonVersion"; exit 1 }
Write-Host "Python version: $pythonVersion"

# Build frontend
Push-Location ../frontend
if (Test-Path package-lock.json) { npm ci } else { npm install }
if ($LASTEXITCODE -ne 0) { Write-Error 'npm install failed'; exit 1 }
npm run build
if ($LASTEXITCODE -ne 0) { Write-Error 'Frontend build failed'; exit 1 }
Pop-Location

# Alembic upgrade
Push-Location ../backend
. .\.venv\Scripts\Activate.ps1
alembic upgrade head
if ($LASTEXITCODE -ne 0) { Write-Error 'Alembic upgrade failed'; exit 1 }
Pop-Location

# Print Vercel copy sheet
$envPath = "../frontend/.env.example"
$apiBase = if (Test-Path $envPath) { (Get-Content $envPath | Select-String 'NEXT_PUBLIC_API_BASE_URL' | ForEach-Object { $_.ToString().Split('=')[1].Trim() }) } else { 'http://localhost:8000' }

Write-Host "\n=== VERCEL COPY SHEET ==="
Write-Host "Root Directory: frontend"
Write-Host "Framework: Next.js"
Write-Host "Node: 20.x"
Write-Host "Env:"
Write-Host "  NEXT_PUBLIC_API_BASE_URL = $apiBase"
Write-Host "==========================\n"
