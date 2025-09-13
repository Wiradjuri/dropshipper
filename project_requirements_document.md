# Dropshipper – PRD (Agent Brief)

**MVP Goal:** Storefront → cart → Stripe Checkout → order recorded `paid` → receipt email → mock supplier adds `tracking_number`.

**Tech:** Next.js (TS, App Router), Tailwind / FastAPI (Py 3.12), async SQLAlchemy, Alembic (SQLite dev → Postgres later), Stripe Checkout.

**Guardrails for agents**

* Additive edits; avoid destructive refactors unless localized.
* SQLite-safe Alembic: `render_as_batch=True`; use **unique indexes** (not `ALTER ... ADD CONSTRAINT`).
* Don’t bump major package versions to “fix” peer deps; pin Next 14.x + React 18.x if needed.
* Prices/stock are **server-authoritative**; never trust client totals.
* Access tokens in **httpOnly** cookies; strict CORS (`FRONTEND_ORIGIN`).

**Operating context**

* OS: Windows / PowerShell.
* Backend dir: `backend\` (venv in `.venv`), Frontend dir: `frontend\`.

**Stop criteria (“Done”)**

* Can create a product, pay with Stripe test card **4242 4242 4242 4242**, order status becomes `paid`, a receipt email is queued/sent (provider sandbox), and `tracking_number` appears later from the mock supplier.

---

## Agent Execution Plan (T1–T6)

> For each task: output full file paths + complete files; run the given PowerShell commands; paste outputs; if anything fails, fix and retry automatically.

### T1 — Health checks

* **Backend:** ensure `GET /health` → `{"status":"ok"}`.
* **Frontend:** home page fetches and renders backend health.
* **Run/verify**

  ```powershell
  cd backend; . .\.venv\Scripts\Activate.ps1; $env:PYTHONPATH="."; alembic upgrade head; uvicorn app.main:app --reload --port 8000
  cd ../frontend; npm install; npm run dev
  # Verify: http://localhost:8000/health and http://localhost:3000
  ```

### T2 — Products CRUD

* **Backend:** SQLAlchemy model, Pydantic v2 schemas, repo, router; **SQLite-safe** migration with a **unique index on `sku`** (no `ALTER … ADD CONSTRAINT`).
* **Frontend:** `/ (admin)/products` list/create/edit/delete using `src/lib/api.ts`.
* **Run/verify**

  ```powershell
  cd backend; . .\.venv\Scripts\Activate.ps1; $env:PYTHONPATH="."; alembic upgrade head; uvicorn app.main:app --reload --port 8000
  # In new terminal
  cd frontend; npm install; npm run dev
  # Verify: GET http://localhost:8000/products; UI at http://localhost:3000/(admin)/products
  ```

### T3 — Cart + Order creation

* **Frontend:** `src/context/cart.tsx` with `addItem/removeItem/updateQty` (persist to localStorage); `/cart` shows items + preview totals.
* **Backend:** `POST /orders` recomputes totals from DB prices; `GET /orders/{id}` returns items/totals.
* **Run/verify**

  ```powershell
  # Use REST file dev/cart-orders.http (create if missing) to:
  # 1) create products, 2) create order, 3) fetch order by id
  ```

### T4 — Stripe Checkout + webhook

* **Backend:** `POST /checkout/session` (server-validates items/qty, creates Stripe session), `POST /webhooks/stripe` (idempotent; mark `paid`).
* **Frontend:** Checkout button redirects to `checkout_url`.
* **Run/verify**

  ```powershell
  # Backend .env needs STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET (test keys)
  # Pay with 4242 4242 4242 4242; order transitions to paid
  ```

### T5 — Supplier mock + poller

* **Backend:** `integrations/base.py` + `integrations/mock_supplier.py` (`place_order`, `get_tracking`).
  On `paid`, store `supplier_order_id`; APScheduler polls and sets `tracking_number`, then `fulfilled`.
* **Verify:** within a couple of minutes, `GET /orders/{id}` shows `tracking_number`.

### T6 — Emails

* **Backend:** SendGrid/Postmark service; send receipt on `paid`.
* **Run/verify:** provider sandbox/test mode shows receipt delivered.

---

# Dropshipper – Product Requirements Document (PRD)

**Doc version:** 1.0
**Status:** Draft → Working
**Owner:** Product/Engineering (Brad)
**Last updated:** 2025-09-13
**Related repos:** `frontend/` (Next.js), `backend/` (FastAPI)
**Environments:** `local`, `staging`, `production`

---

## 1) Overview

### 1.1 Product summary

Dropshipper is an e-commerce web app that enables small merchants to list products, accept payments, and fulfill orders via third-party suppliers. The app provides a streamlined admin experience and a fast, mobile-first storefront.

### 1.2 Goals

* Enable a merchant to go from **zero to first sale** in under **1 day**.
* Provide a **fast storefront** (Core Web Vitals pass), **secure checkout**, and **automated fulfillment** via supplier integrations.
* Make operations manageable for a solo operator (inventory, orders, emails) without custom code.

### 1.3 Non-goals

* Marketplace/multi-vendor features (one storefront per merchant only).
* Custom page builder or theme marketplace in v1.
* Native mobile apps (web-first PWA is sufficient).

---

## 2) Success Metrics (KPIs)

* **Time to Live:** New merchant setup (domain, payment, products) in ≤ 24 hours.
* **Performance:** Storefront LCP ≤ 2.5s (p75), TTI ≤ 3.5s (p75), API p95 latency ≤ 300ms.
* **Conversion:** Checkout completion ≥ 60% once Stripe page is reached.
* **Reliability:** API uptime ≥ 99.9% monthly (prod).
* **Error budget:** ≤ 0.5% failed orders/month.
* **Operational efficiency:** < 10 minutes/day required for order processing at 10 orders/day.

---

## 3) Users & Roles

* **Customer (anonymous/authenticated):**

  * Browse catalog, search/filter, add to cart, checkout.
  * View order confirmation; optional account to view history.
* **Admin (merchant):**

  * CRUD products, manage inventory, prices, and product status.
  * Review orders and statuses (created/paid/fulfilled/cancelled).
  * Configure payments (Stripe), email provider (SendGrid/Postmark), and supplier credentials.
* **System:** background jobs for order forwarding and tracking updates.

---

## 4) Scope (v1)

### 4.1 Storefront (Customer)

* Home, Category/listing, Product detail.
* Cart page with quantity updates and persisted cart.
* Checkout entry → **Stripe Checkout** (server-validated prices).
* Order success/cancel pages; email receipt.

### 4.2 Admin

* Products list/detail:

  * Fields: id, title, description, images\[], price, SKU, inventory, is\_active.
* Orders list/detail:

  * Status flow: created → paid → fulfilled/cancelled.
  * Supplier forwarding status + tracking number (if available).
* Basic auth (JWT) with roles (`admin`, `customer`) and httpOnly cookies.
* Settings: Stripe keys, email provider key, supplier mode (`mock` for v1).

### 4.3 Integrations

* **Payments:** Stripe Checkout + webhook for `checkout.session.completed`.
* **Email:** SendGrid or Postmark for receipts and abandoned cart reminders.
* **Supplier:** Mock supplier (place order + query tracking). Real supplier adapters in v2.

---

## 5) Functional Requirements

### 5.1 Catalog

* **FR-CAT-1:** Admin can create/edit/delete products.
* **FR-CAT-2:** Storefront lists only `is_active = true` products with pagination and search by `q` (title/description).
* **FR-CAT-3:** Product detail shows title, images, description, price, stock (if > 0) and add-to-cart.

### 5.2 Cart & Checkout

* **FR-CART-1:** Cart is client-side (localStorage) + server echo when creating order.
* **FR-CART-2:** Add/update/remove items with qty ≥ 1 and ≤ MAX\_QTY (default 10).
* **FR-CKO-1:** Backend validates prices/stock; **never trusts client totals**.
* **FR-CKO-2:** Stripe Checkout session created with authoritative prices and qty.
* **FR-CKO-3:** On successful payment, order moves to `paid`, email receipt is sent.

### 5.3 Orders & Fulfillment

* **FR-ORD-1:** Admin can view orders with line items and totals.
* **FR-ORD-2:** On `paid`, system calls Supplier adapter `place_order()` and stores `supplier_order_id`.
* **FR-ORD-3:** Background job polls supplier `get_tracking()`; sets `tracking_number` and marks `fulfilled` when available.

### 5.4 Authentication & Authorization

* **FR-AUTH-1:** JWT access/refresh tokens; access in httpOnly cookie.
* **FR-AUTH-2:** Admin routes protected (`require_admin`).
* **FR-AUTH-3:** Token refresh rotates before expiry; logout clears cookies.

### 5.5 Notifications

* **FR-MAIL-1:** Receipt email includes order id, items, totals, and tracking link (if known).
* **FR-MAIL-2:** Abandoned cart: heartbeat from client; if stale, send reminder (rate-limited, opt-out respected).

---

## 6) Non-Functional Requirements (NFRs)

* **Security:** OWASP ASVS L1; CSRF-resistant (httpOnly + sameSite where relevant), strong CORS rules, input validation, rate limiting, request IDs, structured logging.
* **Privacy:** No PII beyond email/address for shipping; respect unsubscribe headers.
* **Accessibility:** WCAG 2.1 AA; keyboard nav, ARIA labels, color contrast.
* **Performance:** See KPIs. Image optimization (Next Image), caching with SWR/HTTP cache headers, DB indexes on SKU, created\_at.
* **SEO:** Semantic HTML, metadata per page, OpenGraph/Twitter tags, sitemap, robots.txt.
* **Scalability:** Stateless API; background jobs scalable (APScheduler or external queue later).
* **Observability:** Structured logs, error monitoring (Sentry/OpenTelemetry), health endpoints.
* **Compliance (payments):** PCI handled by Stripe; no card data stored.

---

## 7) Information Architecture & Data Model

### 7.1 Entities (v1)

* **Product**: `id:int`, `title:str`, `description:str`, `images:list[str]`, `price:Decimal-as-string`, `sku:str unique`, `inventory:int`, `is_active:bool`, `created_at`, `updated_at`.
* **CartItem** (server echo / order creation): `product_id:int`, `qty:int`, `unit_price:string`.
* **Order**: `id:int`, `status:enum("created","paid","fulfilled","cancelled")`, `subtotal:string`, `shipping:string`, `total:string`, `created_at`, `updated_at`, `supplier_order_id:optional`, `tracking_number:optional`.
* **OrderItem**: `id:int`, `order_id:int`, `product_id:int`, `qty:int`, `unit_price:string`.
* **User**: `id:int`, `email:str unique`, `password_hash:str`, `role:enum("admin","customer")`, timestamps.

### 7.2 Relationships

* `Order 1..* OrderItem`
* `Product 1..* OrderItem`
* `Product.sku` unique index.

### 7.3 Indexes

* `products.sku` (unique)
* `products.created_at`
* `orders.created_at`
* `order_items.order_id`, `order_items.product_id`

---

## 8) APIs (initial surface)

Base URL (local): `http://localhost:8000`

### 8.1 Health

* `GET /health` → `{status:"ok"}`

### 8.2 Products

* `GET /products?q&is_active&limit&offset`
* `GET /products/{id}`
* `POST /products` *(admin)*
* `PUT /products/{id}` *(admin)*
* `DELETE /products/{id}` *(admin)*

### 8.3 Cart (server echo)

* `POST /cart/items` body `{product_id, qty}` → returns computed cart snapshot
* `DELETE /cart/items/{id}` → returns snapshot
* `GET /cart` → computed snapshot

### 8.4 Orders

* `POST /orders` body `{items:[{product_id,qty}], shipping, email?}` → `OrderRead`
* `GET /orders/{id}` → `OrderRead`

### 8.5 Checkout

* `POST /checkout/session` body `{items:[{product_id,qty}], email?}` → `{checkout_url}`
* `POST /webhooks/stripe` (Stripe only)

### 8.6 Auth

* `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`

---

## 9) UX Flows (happy paths)

### 9.1 Browse → Cart → Checkout (Customer)

1. Visit Home → view products → open Product detail.
2. Add to cart → go to Cart.
3. Press Checkout → server validates, creates Stripe session, redirects to Stripe.
4. Payment success → redirect to Success page → email receipt.

**Edge cases:** out-of-stock, price changed, Stripe failure, timeout, network loss → friendly error + retry guidance.

### 9.2 Admin: Add Product

1. Login → Admin Products page.
2. Create product (required: title, price, sku) → set active.
3. Product appears on storefront listing.

### 9.3 Admin: Order Review

1. Open Orders list → open order detail.
2. See `paid` orders; if `tracking_number` present show link; if none, show “Awaiting supplier”.

---

## 10) Security Requirements

* **Auth:** JWT access (short-lived) + refresh tokens; store access token in httpOnly cookie. Lock down admin routes.
* **Input validation:** Pydantic schemas (backend) and client form constraints.
* **Rate limiting:** Login, cart modification, checkout session creation.
* **CORS:** Allow only the configured frontend origin.
* **Headers:** HSTS (prod), `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, CSP (tighten progressively).
* **Secrets:** `.env` files not committed; secrets stored in platform key vault in prod.

---

## 11) Analytics & Telemetry

* **Events:** Product view, add to cart, begin checkout, session created, payment success/fail.
* **Metrics:** Orders/day, revenue, email delivery rates, abandoned cart recovery rate.
* **Error tracking:** Sentry/OTel traces for FastAPI & Next.js.
* **Dashboards:** Basic charts in an admin “Analytics” tab (v2).

---

## 12) SEO & Content

* Canonical URLs, sitemap.xml, robots.txt.
* Structured data (Product schema) on PDP.
* Descriptive meta titles/descriptions per page.
* Open Graph/Twitter cards for product sharing.

---

## 13) Accessibility

* Keyboard focus order and visible focus states.
* Images: alt text; product images have meaningful alts.
* Form labels, error messages, ARIA roles for dialogs.
* Color contrast ≥ 4.5:1, prefers-reduced-motion.

---

## 14) Performance Budgets

* **Storefront pages:** HTML < 60KB gzipped, JS < 200KB (route-level).
* **Image sizes:** WebP/AVIF responsive; largest < 200KB on mobile.
* **API latency:** p95 ≤ 300ms; cache list endpoints (where safe) with ETag/Cache-Control.

---

## 15) Operational Model

* **Jobs:** Background poller (APScheduler) every 5 minutes for tracking updates.
* **Logging:** `structlog` or `loguru` JSON logs with request IDs and user IDs where applicable.
* **Runbooks:** Error triage, webhook replay steps, supplier outage fallback (email the supplier and mark “awaiting fulfillment”).

---

## 16) Testing Strategy

* **Unit tests:** Repos/services (prices, totals, inventory validation).
* **API tests:** `pytest` + `httpx.AsyncClient`.
* **Frontend tests:** Vitest + React Testing Library for cart logic and components.
* **E2E (v2):** Playwright (critical flows only).
* **CI:** GitHub Actions for lint, test, build; fail on coverage < target.

---

## 17) Release Plan

### 17.1 Milestones

1. **M1 – Core catalog** (done/in progress): products CRUD, list/search.
2. **M2 – Cart & Orders**: server-validated totals, order creation.
3. **M3 – Payments**: Stripe Checkout + webhook; success/cancel pages; email receipts.
4. **M4 – Supplier mock**: place order + tracking poller; admin visibility.
5. **M5 – Auth & Admin hardening**: JWT, roles, protected routes.
6. **M6 – Security/Observability**: headers, rate limiting, structured logs, error monitor.
7. **M7 – Deploy**: Docker, Compose, prod on Railway/Fly (API) + Vercel (frontend), Postgres migration.

### 17.2 Rollout

* Staging with test Stripe keys and mock supplier.
* Smoke tests on each deploy; verify webhooks with Stripe CLI.
* Canary release (small % traffic) if needed.

---

## 18) Risks & Mitigations

* **Payment failures / webhook delays:** Retry logic, idempotency keys, replay webhooks.
* **Supplier latency:** Queue requests, present ETA; manual override for fulfillment.
* **Inventory drift:** Reconcile after each paid order; alerts if negative stock.
* **Spam/abuse:** Rate limit sensitive endpoints; captcha on abusive IPs (v2).

---

## 19) Open Questions

* Is multi-currency required in v1? (Default AUD or USD.)
* Do we support customer accounts at launch or email-only receipts?
* Minimum SEO content per product?
* Which supplier(s) for v2 real integration?

---

## 20) Acceptance Criteria (Go/No-Go)

* Can create 3 products; storefront lists them; PDP renders with images.
* Add to cart → checkout → pay via Stripe test card **4242 4242 4242 4242**; order shows as `paid`.
* Email receipt delivered to test inbox.
* Background job sets tracking on at least one mock order.
* Core Web Vitals passing in Lighthouse mobile (p75).
* All tests green in CI; error budget in staging ≤ thresholds for 1 week.

---

## 21) Appendix

### 21.1 .env (local examples)

**Backend**

```
DATABASE_URL=sqlite+aiosqlite:///./app.db
FRONTEND_ORIGIN=http://localhost:3000
DISABLE_AUTH=false
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

**Frontend**

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 21.2 Locations

* `project_requirements_document.md` ← this file (authoritative PRD)
* `/docs/prd.md` ← optional human-readable copy
* `/docs/prd-agent.md` ← optional pointer/mini brief for agents

---

**End of PRD**
