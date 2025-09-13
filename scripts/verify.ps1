# scripts/verify.ps1
# Runs a compact suite of checks. Exits non-zero on failure.

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location (Join-Path $repoRoot "..")  # ensure script can run from scripts/

function Step($name, [ScriptBlock]$fn) {
  Write-Host "==> $name"
  & $fn
  Write-Host "<== $name : OK`n"
}

function Run($cmd) {
  Write-Host "  $ $cmd"
  powershell -NoLogo -NoProfile -Command $cmd
}


# 0) Preflight: Check NEXT_PUBLIC_API_BASE_URL in frontend/.env.example
$envPath = "frontend/.env.example"
if (-not (Test-Path $envPath)) { Write-Error ".env.example missing in frontend"; exit 1 }
$apiBase = (Get-Content $envPath | Select-String 'NEXT_PUBLIC_API_BASE_URL' | ForEach-Object { $_.ToString().Split('=')[1].Trim() })
if (-not $apiBase) { Write-Error "NEXT_PUBLIC_API_BASE_URL missing in .env.example"; exit 1 }

# Tooling (optional Trunk)
if (Test-Path ".trunk\trunk.yaml") {
  Step "Trunk install tools" { Run "trunk tools install" }
}

# 1) Backend: deps, alembic, import check
Step "Backend deps" {
  if (-not (Test-Path "backend\.venv\Scripts\Activate.ps1")) {
    Run "cd backend; python -m venv .venv"
  }
  Run "cd backend; . .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}
Step "Alembic upgrade head" {
  Run "cd backend; . .\.venv\Scripts\Activate.ps1; `$env:PYTHONPATH='.'; alembic upgrade head"
}
Step "Backend import check" {
  Run "cd backend; . .\.venv\Scripts\Activate.ps1; python -c `"import app.main as m; print('app:', m.app.title)`""
}

# 2) Frontend: install, typecheck/build
Step "Frontend deps" {
  Run "cd frontend; npm install"
}
# Prefer build to catch type errors; fail if build fails
try {
  Step "Frontend build" { Run "cd frontend; npm run build" }
}
catch {
  Write-Error 'Frontend build failed'; exit 1
}

# 3) Linters (Trunk, if present)
if (Test-Path ".trunk\trunk.yaml") {
  Step "Trunk check" { Run "trunk check --ci" }
}

# 4) Tests (optional)
if (Test-Path "backend\tests") {
  Step "Backend tests" { Run "cd backend; . .\.venv\Scripts\Activate.ps1; pytest -q" }
}
if (Test-Path "frontend\package.json") {
  $pkg = Get-Content "frontend\package.json" -Raw | ConvertFrom-Json
  if ($pkg.scripts.PSObject.Properties.Name -contains "test") {
    Step "Frontend tests" { Run "cd frontend; npm run test --silent" }
  }
}

Write-Host "All verification steps completed."
Pop-Location
