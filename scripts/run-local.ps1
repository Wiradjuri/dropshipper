# Runs backend + frontend locally on Windows/PowerShell.
# - Installs deps
# - Applies Alembic migrations (SQLite-safe)
# - Starts Uvicorn on :8000 and Next.js on :3000 in background jobs

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $repo "..")
Set-Location $root

function Ensure-File($path, $content) {
  if (-not (Test-Path $path)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
    Set-Content -Path $path -Value $content -Encoding UTF8
    Write-Host "Created $path"
  }
}

# --- Ensure .envs exist (safe defaults for local) ---
Ensure-File "backend\.env" @"
DATABASE_URL=sqlite+aiosqlite:///./app.db
FRONTEND_ORIGIN=http://localhost:3000
DISABLE_AUTH=true
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder
"@

Ensure-File "frontend\.env.local" @"
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
"@

# --- Backend job ---
if (-not (Test-Path "backend\.venv\Scripts\Activate.ps1")) {
  Write-Host "Creating backend venv..."
  powershell -NoLogo -NoProfile -Command "cd backend; python -m venv .venv"
}

$backend = Start-Job -Name "dropshipper-backend" -ScriptBlock {
  $ErrorActionPreference = "Stop"
  Set-Location $using:root\backend
  . .\.venv\Scripts\Activate.ps1
  $env:PYTHONPATH="."
  pip install -r requirements.txt
  alembic upgrade head
  Write-Host "Starting Uvicorn on http://localhost:8000 ..."
  uvicorn app.main:app --reload --port 8000
}

# --- Frontend job ---
$frontend = Start-Job -Name "dropshipper-frontend" -ScriptBlock {
  $ErrorActionPreference = "Stop"
  Set-Location $using:root\frontend
  npm install
  Write-Host "Starting Next.js dev server on http://localhost:3000 ..."
  npm run dev
}

Write-Host ""
Write-Host "Jobs started:"
Write-Host "  Backend  : (Get-Job -Name dropshipper-backend) | Receive-Job -Keep"
Write-Host "  Frontend : (Get-Job -Name dropshipper-frontend) | Receive-Job -Keep"
Write-Host ""
Write-Host "Open:"
Write-Host "  API Health : http://localhost:8000/health"
Write-Host "  API Docs   : http://localhost:8000/docs"
Write-Host "  Frontend   : http://localhost:3000"
Write-Host ""
Write-Host "Tip: to stream logs, run:"
Write-Host "  Receive-Job -Name dropshipper-backend -Keep"
Write-Host "  Receive-Job -Name dropshipper-frontend -Keep"
