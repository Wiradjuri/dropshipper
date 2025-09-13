# Repo Rules: Non-Stop Verify & Fix

## Global behavior
- Operate in **non-stop execution**. Do **not** pause for confirmation.
- If any step fails, **patch and retry automatically**, then continue.
- OS: **Windows / PowerShell**
- Only edit inside `/backend` and `/frontend` (and docs/.github/scripts as needed).
- Do not bump major versions to “fix” peers: prefer Next 14.x + React 18.x. Keep FastAPI/SQLAlchemy/Alembic pins compatible with SQLite.
- Alembic must be **SQLite-safe** (`render_as_batch=True`) and use **UNIQUE INDEX** for `sku` (not `ALTER ADD CONSTRAINT`).
- Prices/stock are **server-authoritative**; never trust client totals.
- Auth: access token in **httpOnly** cookie; strict CORS via `FRONTEND_ORIGIN`.

## Source of truth
- `project_requirements_document.md` (full PRD + acceptance criteria)
- `docs/prd-agent.md` (agent brief, optional)
- `docs/verification-checklist.md` (machine-friendly checklist)
- `scripts/verify.ps1` (PowerShell verification script)

## What to do
1. **Gap check** the repo against the PRD & checklist. If something is missing/incomplete, scaffold/implement it.
2. Run `scripts/verify.ps1`. If it fails, **fix code/config**, then re-run.
3. Repeat until all checks pass.

## Allowed commands (typical)
- Backend: `cd backend; . .\.venv\Scripts\Activate.ps1; $env:PYTHONPATH="."; pip install -r requirements.txt; alembic upgrade head; uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend; npm install; npm run build || npm run dev`
- Quality: `trunk tools install; trunk check --ci` (if .trunk/trunk.yaml exists)
- Tests: `pytest -q` (if tests exist), `npm run test` (if configured)

## Output contract
For each iteration, provide:
- **Actions** (bulleted)
- **Files changed** (paths only)
- **Commands run** (compact) + key results
- **Next step** (or “verifications passed”)

## Finish tokens
- When PRD features are complete: `__PRD_COMPLETE__`
- When zero errors remain (build/type/lint/tests): `__ZERO_ERRORS__`
- When both achieved, print: `__ALL_TASKS_COMPLETE__`
