# Dropshipper – PRD (Agent Brief)
MVP: Storefront → cart → Stripe Checkout → order `paid` → receipt → mock supplier `tracking_number`.
Tech: Next.js (TS, App Router, Tailwind) / FastAPI (Py 3.12), async SQLAlchemy, Alembic (SQLite dev), Stripe Checkout.
Guardrails: additive edits; SQLite-safe migrations; unique index on sku; server-authoritative totals; httpOnly cookie; strict CORS.
Stop criteria: Stripe 4242 test flows end-to-end; tracking appears later; print `__ALL_TASKS_COMPLETE__`.
