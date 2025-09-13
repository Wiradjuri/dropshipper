# Verification Checklist (Dropshipper)

## Functional (PRD)
- [ ] Products CRUD API (list/search, get, create, update, delete) with SQLite-safe unique index on `sku`.
- [ ] Admin products UI page.
- [ ] Cart (client) + Orders API: POST /orders recomputes totals, GET /orders/{id}.
- [ ] Stripe Checkout session + webhook marks order `paid`.
- [ ] Receipt email queued/sent (stub/sandbox ok for local).
- [ ] Supplier mock: place_order on `paid`; poller sets `tracking_number` → order `fulfilled`.

## Security / Config
- [ ] CORS locked to FRONTEND_ORIGIN; httpOnly cookies for access token.
- [ ] Alembic `render_as_batch=True`; no ALTER ADD CONSTRAINT on SQLite.

## Acceptance (Go/No-Go)
- [ ] Can create 3 products; storefront lists them; PDP renders images.
- [ ] 4242 test card completes; order status becomes `paid`.
- [ ] Receipt email observed (sandbox/stub logs).
- [ ] `tracking_number` appears later from mock supplier.

## Quality Gates
- [ ] Backend builds/imports; `alembic upgrade head` succeeds.
- [ ] Frontend builds (`npm run build`) with **0 type errors**.
- [ ] Linters pass (Trunk or project linters).
- [ ] Tests pass (pytest / Vitest if present).

## Smoke URLs (local)
- [ ] http://localhost:8000/health → `{"status":"ok"}`
- [ ] http://localhost:8000/docs
- [ ] http://localhost:3000
- [ ] Admin products: http://localhost:3000/(admin)/products
