# Repo Rules: Non-Stop Build Mode

## Global behavior
- Operate in **non-stop execution**. Do **not** wait for confirmation between tasks. 
- If a command fails, **patch and retry automatically**, then proceed.
- Use **Windows / PowerShell** terminals.
- Only edit inside `/backend` and `/frontend`.
- **No major version bumps** to “fix” deps: prefer `next@14.x`, `react@18`, `react-dom@18`. 
- SQLite-safe Alembic (`render_as_batch=True`). Use **UNIQUE INDEX** for `sku` (no `ALTER ADD CONSTRAINT`).
- **Server-authoritative** prices/stock; never trust client totals.
- Access token in **httpOnly** cookie; CORS via `FRONTEND_ORIGIN`.

## Tasks to execute sequentially (no pauses)
T2 — Products CRUD
T3 — Cart + Orders
T4 — Stripe Checkout + webhook (use placeholders if secrets missing)
T5 — Supplier mock + poller
T6 — Emails (use sandbox/stub if secrets missing)

## Secrets rule
If a real secret is required, **scaffold with placeholders** and CONTINUE. Do not stop or ask questions.

## Output contract
For each task, produce a compact log:
- “Actions” (bullets), “Files changed” (paths only), “Commands run” (short), “Verification” (URLs/REST + brief result).
Then immediately move to the next task.

## Finish token
When all tasks are done, print exactly:
`__ALL_TASKS_COMPLETE__`
