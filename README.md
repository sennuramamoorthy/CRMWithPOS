# CRM with POS

Multi-tenant CRM + Point-of-Sale system. Each tenant (client) has its own
application name and logo, plus their own warehouses, distributors, products,
customers, orders, invoices, and payments — all isolated by `tenant_id` inside
a single shared Postgres database.

## Features

- **Per-client branding** — upload a logo, set the application name and
  primary color from Settings; it applies across the sidebar, header, and
  browser tab.
- **Multi-warehouse inventory** — per-warehouse stock levels for every
  product, with manual adjustments and automatic decrement at checkout.
- **Distributors** — track suppliers and link products to them.
- **POS** — searchable product grid, cart, tax/discount, walk-in or named
  customer; checkout creates an order, deducts stock, and generates an invoice.
- **Invoices & payments** — record partial or full payments; invoice status
  rolls forward from `unpaid` → `partial` → `paid`.
- **Reports & dashboard** — 30-day revenue, outstanding A/R, low-stock count,
  daily revenue chart.
- **JWT auth** with `admin` / `manager` / `cashier` roles.

## Stack

- **Backend**: FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL 16 · JWT
- **Frontend**: Vite · React 18 · TypeScript · TailwindCSS · React Router
  (UI primitives are inline shadcn-style components — no shadcn CLI)
- **Tooling**: docker-compose · Makefile · Nginx (production frontend)

## Prerequisites

- Python 3.11+
- Node 20+
- Docker & Docker Compose
- GNU Make

## Quick start (local dev)

```bash
make install        # creates venv, pip install, npm install, copies .env files
make db-up          # starts Postgres in Docker
make migrate        # applies Alembic migrations
make seed           # creates demo tenant + admin user
make dev            # runs backend (:8000) + frontend (:5173) in parallel
```

Then open <http://localhost:5173> and sign in:

- **Email**: `admin@acme.test`
- **Password**: `admin123`

API docs: <http://localhost:8000/docs>

Run `make help` to see every available target.

### One-time vs daily

| Daily              | Occasional                                  |
| ------------------ | ------------------------------------------- |
| `make dev`         | `make migrate` after pulling model changes  |
| `make db-up`       | `make migration m="add column"` after edits |
|                    | `make reset-db` to wipe and reseed          |

## Project layout

```
.
├── backend/           # FastAPI app, SQLAlchemy models, Alembic migrations
│   ├── app/
│   │   ├── models/    # tenant, user, warehouse, distributor, product,
│   │   │              # stock, customer, order, invoice, payment
│   │   ├── routers/   # REST endpoints, scoped by tenant_id
│   │   ├── schemas/   # Pydantic request/response models
│   │   └── core/      # security (JWT, hashing) + tenant-scoped CRUD helpers
│   ├── alembic/
│   └── Dockerfile
├── frontend/          # Vite + React + TS app
│   ├── src/
│   │   ├── components/ui/   # Button, Card, Dialog, DataTable, ...
│   │   ├── contexts/        # AuthContext, TenantContext (branding)
│   │   ├── pages/           # POS, Orders, Invoices, Settings, ...
│   │   └── lib/             # axios client + types
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml         # dev DB only
├── docker-compose.prod.yml    # full prod stack (db + backend + frontend)
├── Makefile
└── CLAUDE.md          # architecture notes for future Claude sessions
```

## Testing & quality

```bash
make lint           # tsc --noEmit on the frontend
make test           # runs pytest / vitest if present (currently a no-op)
```

There is no test suite yet. Add `pytest` + `httpx` under `backend/tests/`
and `vitest` + `@testing-library/react` in the frontend when you start
adding tests — the `make test-backend` / `make test-frontend` targets are
already wired to pick them up.

## Building & deployment

The production stack runs as three containers: `db` (Postgres),
`backend` (FastAPI behind Uvicorn), and `frontend` (built Vite bundle
served by Nginx with an SPA fallback). State lives in two named volumes:
`crm_pg` (database) and `crm_uploads` (tenant logos).

### 1. Build and push images

```bash
make docker-push \
  REGISTRY=ghcr.io/your-org \
  IMAGE_TAG=v0.1.0 \
  VITE_API_URL=https://api.your-domain.com
```

`VITE_API_URL` is baked into the frontend bundle at build time — set it to
the URL your browser will use to reach the backend.

### 2. Configure the target host

```bash
cp .env.prod.example .env.prod
$EDITOR .env.prod        # set POSTGRES_PASSWORD, JWT_SECRET, CORS_ORIGINS, ...
```

`.env.prod` is gitignored. The compose file fails fast if `POSTGRES_PASSWORD`
or `JWT_SECRET` is missing.

### 3. Bring it up

```bash
make deploy-pull       # pull latest images from the registry
make deploy-up         # start the stack
make deploy-migrate    # run Alembic upgrade head
make deploy-seed       # first deploy only — create demo tenant
make deploy-logs       # tail logs
```

For subsequent releases:

```bash
make docker-push IMAGE_TAG=v0.2.0
# on the server:
IMAGE_TAG=v0.2.0 make deploy-pull
IMAGE_TAG=v0.2.0 make deploy-restart
IMAGE_TAG=v0.2.0 make deploy-migrate
```

### Reverse proxy / TLS

The default `frontend` container listens on port 80 and the `backend` on
8000 — fine for a private network. For public deployment, front them with
Caddy / Nginx / Traefik terminating TLS and forwarding to the two
containers. Update `CORS_ORIGINS` in `.env.prod` to your public origin.

## Architecture in one paragraph

Every business table carries a `tenant_id` FK with `ON DELETE CASCADE`.
There is **no Postgres row-level security** — isolation is enforced in
code by the `get_current_tenant` FastAPI dependency, which reads the
tenant ID from the JWT, and by the `list_for_tenant` / `get_for_tenant`
helpers used by every router. The frontend's `TenantContext` fetches
`/tenant` after login, sets `document.title`, and writes the brand color
into the `--color-brand` CSS variable so Tailwind's `bg-brand` /
`text-brand-fg` cascade through the whole UI without a rebuild. The
order checkout endpoint is the only multi-table transaction in the
system: it validates stock, decrements per-warehouse `stock_levels`,
creates `Order` + `OrderItem` rows, and generates an `Invoice` — all in
one session.

See **[CLAUDE.md](CLAUDE.md)** for the full architecture writeup, conventions,
and the list of things deliberately not built yet.

## License

Proprietary — for internal client use.
