# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A multi-tenant CRM + Point-of-Sale system. Every tenant (the operator's client)
has its own application name and logo, plus their own warehouses, distributors,
products, customers, orders, invoices, and payments — all isolated by
`tenant_id` inside a single shared Postgres database.

Stack: **FastAPI + SQLAlchemy + Alembic + Postgres** backend · **Vite + React +
TypeScript + Tailwind** frontend, with small inline shadcn-style UI primitives
under `frontend/src/components/ui/`.

## Common commands

### Backend (`backend/`)

```bash
# one-time
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# DB
docker compose up -d db          # from repo root
alembic upgrade head             # apply migrations
python -m app.seeds              # demo tenant + admin (admin@acme.test / admin123)

# Dev server
uvicorn app.main:app --reload    # http://localhost:8000  ·  /docs for Swagger

# New migration (after editing models)
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

### Frontend (`frontend/`)

```bash
npm install
cp .env.example .env             # VITE_API_URL=http://localhost:8000
npm run dev                      # http://localhost:5173
npm run build                    # type-check + production build
npm run lint                     # tsc --noEmit
```

There is no test suite yet — add `pytest` for the backend and
`vitest`/`@testing-library/react` for the frontend when you start adding tests.

## Architecture — the parts that aren't obvious from one file

### Multi-tenancy: `tenant_id` on every business row

Every business table (`users`, `warehouses`, `distributors`, `products`,
`stock_levels`, `customers`, `orders`, `order_items`, `invoices`, `payments`)
has a `tenant_id` FK to `tenants` with `ON DELETE CASCADE`. There is **no
implicit row-level security** in Postgres — isolation is enforced in code by:

1. The `get_current_tenant` dependency in [backend/app/dependencies.py](backend/app/dependencies.py),
   which resolves the tenant from the JWT's `tid` claim.
2. The CRUD helpers in [backend/app/core/crud.py](backend/app/core/crud.py)
   (`list_for_tenant`, `get_for_tenant`) that scope every query by `tenant_id`.

**When you add a new entity, you must:**
- Add `tenant_id` to the model with a FK + index.
- Use `list_for_tenant` / `get_for_tenant` (or hand-write a `where(Model.tenant_id == tenant.id)`).
- Never trust IDs from the client without checking they belong to the current tenant.

### Branding (logo + app name per client)

Lives on `tenants.name`, `tenants.logo_url`, `tenants.primary_color`. Updated via:
- `PATCH /tenant` — name & color (admin only)
- `POST /tenant/logo` — multipart upload, written to `backend/uploads/logos/` and
  served via FastAPI's `/uploads` static mount.

On the frontend, `TenantContext` ([frontend/src/contexts/TenantContext.tsx](frontend/src/contexts/TenantContext.tsx))
fetches `/tenant` after login, sets `document.title` to the tenant name, and writes
`--color-brand` onto `:root` so Tailwind's `bg-brand` / `text-brand-fg` cascade
through the whole UI. The sidebar logo reads from `tenant.logo_url`.

### Orders are the load-bearing transaction

`POST /orders` ([backend/app/routers/orders.py](backend/app/routers/orders.py)) is the
only place where multiple tables move together:

1. Validate warehouse belongs to tenant.
2. For each item: validate product, check `stock_levels` for the chosen
   warehouse, decrement on-hand. Reject the whole request if any line is short.
3. Compute totals, create `Order` + `OrderItem` rows.
4. Generate an `Invoice` for the order (status `unpaid` unless total is 0).

All within a single SQLAlchemy session — commit at the end so it either all
succeeds or nothing changes. `POST /orders/{id}/cancel` returns stock to the
warehouse and voids the invoice.

Payments (`POST /payments`) update `invoices.amount_paid` and recompute
`invoices.status` (`unpaid` → `partial` → `paid`).

### Frontend layering

- `lib/api.ts` — single axios instance with a request interceptor that attaches
  the JWT from localStorage and a 401-handler that redirects to `/login`.
- `contexts/AuthContext` — `user`, `login(email, password)`, `logout()`.
- `contexts/TenantContext` — `tenant`, `logoSrc`, `refresh()`. Calls `refresh`
  whenever the auth user changes; updates CSS vars + `document.title` on tenant load.
- `components/ui/*` — Button, Input, Card, Dialog, DataTable, Badge. Hand-rolled
  shadcn-style primitives — **do not** install the shadcn CLI on top of these.
- `components/CrudPage.tsx` — generic create/edit/delete table for simple
  entities (Warehouses, Distributors, Customers). Products has its own page
  because it needs distributor selection and a per-warehouse stock view.

### CSS variable bridge: brand color

`index.css` defines `--color-brand` and `--color-brand-fg`; `tailwind.config.js`
maps `brand` / `brand-fg` to those variables. `TenantContext` rewrites
`--color-brand` on tenant load. **This is why `bg-brand` works without rebuilding
Tailwind on color change.**

### Alembic initial migration uses `create_all`

[backend/alembic/versions/0001_initial.py](backend/alembic/versions/0001_initial.py)
calls `Base.metadata.create_all(bind=op.get_bind())` to bootstrap the schema.
This works fine for the first migration but **do not extend it** — write
proper `op.create_table` / `op.add_column` migrations from #0002 onward,
generated via `alembic revision --autogenerate`.

## Conventions

- Backend uses Python 3.11+ syntax (`str | None`, `list[...]`, `from __future__`
  is not needed). Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`
  on response models (helper class: `ORMModel`).
- Decimals on the wire are JSON strings — multiply/divide on the frontend with
  `parseFloat`. Currency formatting uses `formatCurrency` in `frontend/src/lib/utils.ts`,
  currently hard-coded to `INR` — change there if your client uses a different currency.
- Role on `users.role`: `admin` | `manager` | `cashier`. Only `admin` can update
  tenant branding (`require_admin` dep). Extend the guard if you add more
  privileged actions.
- File uploads go to `backend/uploads/` (gitignored). For production deployments,
  replace this with object storage (S3/GCS) and update `tenants.logo_url` to the
  CDN URL — the frontend already handles absolute URLs implicitly via the
  `API_URL` prefix in `TenantContext`.

## Things deliberately not built yet

- No tests. Add `pytest` + `httpx` for backend and `vitest` for frontend.
- No refresh tokens — JWT TTL is 12h via `JWT_EXPIRES_MINUTES`.
- No tenant signup flow — tenants must be created via the seed script or DB.
- No purchase orders / receiving — `stock_levels` are only adjusted via the
  manual "Adjust stock" dialog or by sales.
- No PDF invoice rendering — `invoices` are data only.
- Currency is hard-coded to INR in `formatCurrency`. Make it a tenant setting if
  you go multi-region.
