## How to resume work

When continuing development in a new session:

1. Start by reviewing:
   - docs/backend_architecture.md
   - docs/feedback_workflow.md

2. Focus on:
   - "Sprint checkpoint" section (current state)
   - "Next sprint priorities" section

3. Then continue from the first unfinished item

---

# Backend Architecture

## Purpose

This document describes the structure of the backend and separation of responsibilities.

---

## High-level layers

The backend is divided into several logical layers:

### 1. Web layer (`app/web`)
Purpose:
- Render HTML pages (Jinja templates)
- Handle browser-based interactions
- Return `TemplateResponse` or `RedirectResponse`

Examples:
- `/feedback`
- `/admin/feedback`
- `/admin/feedback/{id}/send-email`
- `/admin/products`

---

### 2. API layer (`app/api/v1`)
Purpose:
- Provide JSON endpoints
- Used by frontend or external clients
- Return structured data (Pydantic models)

Examples:
- `/v1/check-purchase`
- `/v1/feedback`

---

### 3. Service layer (`app/services`)
Purpose:
- Contain business logic
- Independent from HTTP (no Request/Response)
- Reusable across Web and API

Examples:
- `send_feedback_reply`
- `toggle_feedback_publish`

Rules:
- Services may raise `HTTPException`
- Services operate on database models
- Services should not render templates

---

### 4. Repository layer (`app/repositories`)
Purpose:
- Encapsulate database access
- Provide reusable DB queries

Examples:
- `FeedbackAdminRepository`
- `ProductsRepository`

---

### 5. Core layer (`app/core`)
Purpose:
- Infrastructure
- Database engine, session
- Config, logging, i18n

---

### 6. Dependencies (`app/dependencies`)
Purpose:
- Dependency Injection (DI)
- Provide shared dependencies (e.g. DB session)

Important rule:
- Use `get_db` from this module everywhere
- Do not duplicate dependency functions

---

## Request flow

Typical flow:

Web route → Service → Repository → DB

or

API route → Service → Repository → DB

---

## Design principles

- Keep routes thin (no business logic)
- Move logic to services
- Avoid duplication
- Use a single DI entry point
- Keep layers independent

---

## How to implement new features

When adding new functionality, follow this order:

### 1. Define business logic in service

```python
def some_business_action(db: Session, ...):
    ...
```

---

### 2. Use service in route

Web route:
- call service
- return `TemplateResponse` or `RedirectResponse`

API route:
- call service
- return JSON

---

### 3. Use repository inside service

- do not access DB directly from routes
- use repository methods for queries

---

### 4. Add tests

Prefer testing services:

- test business logic directly
- verify DB changes
- verify exceptions (status_code, detail)

Optionally:
- add route tests for critical endpoints

---

## What NOT to do

Avoid:

- putting business logic in routes
- duplicating logic across routes
- creating multiple `get_db` implementations
- mixing HTML rendering with business rules

---

## Refactoring rule

If a route starts to contain:

- multiple `if` conditions
- validation logic
- DB updates

→ move this logic to a service

---

## Sprint checkpoint: admin feedback refactoring and tests

### Completed:

- unified `get_db` usage via `app.dependencies`
- removed duplicate DB dependency definitions
- made `feedback_messages.email` nullable
- added Alembic migration
- introduced service layer
- moved all feedback logic to `feedback_service`
- isolated email sending in `mail_service`

- added full service test coverage:
  - email sending rules
  - publish/unpublish
  - resolve toggle
  - reply draft
  - validation edge cases

- added route-level tests for critical flows
- implemented real SMTP sending (Gmail App Password)

- ensured:
  - clean separation of concerns
  - no real emails in tests (global mocking)

### Architecture decision:

- service tests = business logic
- route tests = wiring only

---

## Sprint 12: current admin products state

### Implemented:

- `ProductsRepository`
- route `/admin/products`
- route `/admin/products/new` (GET)
- template `admin_products_list.html`
- template `admin_product_form.html`
- basic route test for `/admin/products`
- list page is styled and acts as central admin UI

### Current limitations:

- Edit flow is not implemented
- Create form is temporary
- POST create must NOT be finalized yet
- product model still reflects old pricing logic

---

## Sprint checkpoint: product-based reviews

### Completed:

- added `product_id` to feedback
- created FK and migration
- backfilled existing data
- implemented product-scoped reviews
- added `/reviews/{slug}`
- redirect `/reviews → /reviews/smartbudget`
- updated repository, routes, tests

### Architecture decisions:

- reviews are product-scoped
- use `product_id` (not slug) internally
- reviews are scoped per product SKU (e.g. SmartBudget RU vs SmartBudget INT are independent)

---

## Next sprint priorities (after Sprint 15)

### 1. Purchase flow (product family → SKU → checkout)

- introduce `family_slug` in `products`
- group SKUs by product family
- implement purchase options page:
  - `/products/{family_slug}/buy`
- display all available SKUs for selected family:
  - RU / INT
  - Standard / Pro
- link each option to:
  - `/checkout/{product_slug}`

---

### 2. Merchant of Record integration (Paddle)

- create Paddle account
- configure product in Paddle
- implement checkout redirect / link
- define success URL
- plan webhook handling (no full implementation yet)

---

### 3. Sales tracking (admin)

- sales list
- filtering
- purchase validation consistency

---

### 4. Reviews UX improvements

- show preview on landing
- optional rating later

---

### 5. Feedback tightening

- enforce `product_id`
- validate `sale_id ↔ product_id`

---

### 6. Deployment preparation

- connect domain
- choose hosting (VPS / PaaS)
- prepare environment variables
- basic production setup

---

## Product categorical fields design note

Use string + allowed sets:

- edition: {"Standard", "Pro"}
- status: {"in_sale", "in_development", "discontinued"}

### Reason:

- simple
- no migrations
- controlled via UI

---

## Admin UI access design note

### Current:

- no auth
- admin routes hidden from UI

### Rule:

- do NOT expose admin links publicly

### Future:

- add auth
- separate admin layout or conditional rendering

---

## Product model redesign note

## Product family / purchase options note

Current `products` table represents sellable SKUs.

Examples:
- smartbudget-ru-standard
- smartbudget-ru-pro
- smartbudget-int-standard
- smartbudget-int-pro

For purchase option pages, products must be grouped by product family.

Example flow:
- landing page: `/products/smartbudget`
- purchase options page: `/products/smartbudget/buy`
- checkout page: `/checkout/{product_slug}`

Important:
The purchase options page must NOT show all products from the `products` table.
It should show only SKUs that belong to the selected product family.

Reason:
In the future, the site may sell other products, such as:
- books
- templates
- consultations
- other digital products

Possible implementation options:
- add `family_slug` to `products`
- or introduce a separate `product_families` table

MVP direction:
Use `family_slug` on `products` first, because it is simple and enough for grouping SKUs.
A separate `product_families` table can be introduced later if product-family metadata becomes necessary.

### Important:

- SmartBudget RU and SmartBudget INT = separate SKUs
- each has:
  - its own archive
  - its own lifecycle

### Implication:

- product = sellable package, not abstract concept

---

## Product pricing and currency design note

### Proposed MVP fields for `product_prices`

- `id`
- `product_id`
- `currency_code`
- `amount`
- `is_active`
- `created_at`

### MVP rules

- one product SKU may have multiple price records over time
- only one active price per currency for a given product
- initial launch expectation:
  - `SmartBudget RU` → one active `RUB` price
  - `SmartBudget INT` → one active `EUR` price
- future extension:
  - `USD` can be added as an additional currency without changing `products`

### Problem:

- price without currency is invalid

### Decision:

- pricing must be separate from product
- no FX conversion inside app

### Target:

- products → identity
- product_prices → pricing

### Rules:

- one active price per product (MVP)
- allow multiple currencies later

### Initial:

- RU → RUB
- INT → EUR

### Future:

- add USD without redesign

---

## Payments strategy note

### Checkout UX strategy

SmartBudget uses a single checkout page with multiple explicit payment options.

Route:
- /checkout/{product_slug}

Payment options (MVP):
- Russian payments (SBP / local methods)
- International payments (Paddle)
- (optional) crypto

Key rule:
Do NOT auto-detect user country.
User manually selects the working payment method.

Reason:
- avoids incorrect routing (VPN, relocations)
- simplifies debugging
- supports both RU and INT audiences

Design:
- order summary at the top
- vertical list of large payment buttons
- mobile-first layout

### Checkout UI checkpoint

Implemented:
- public route `/checkout/{product_slug}`
- checkout template with i18n keys
- dedicated `checkout.css`
- product summary card:
  - product
  - package
  - edition
  - total
- neutral payment method selection:
  - SBP
  - Russian card / YooMoney / SberPay / T-Pay
  - international card
  - crypto
- no payment provider integration yet

Decision:
- Paddle integration should be handled in a separate sprint after provider setup is ready.
- Current checkout page remains provider-agnostic and uses placeholder links.

### Direction:

- use Merchant of Record

### Why:

- reduce complexity:
  - payments
  - taxes
  - compliance

### Candidates:

- Paddle
- Lemon Squeezy
- Stripe

### Rule:

- keep internal model provider-agnostic
- do not couple DB to payment provider

### Currency design decision (MVP)

- currency is stored as string (`currency_code`)
- no separate `currencies` table in MVP
- avoids unnecessary joins and complexity

Examples:
- "RUB"
- "EUR"

Future:
- introduce `currencies` table only if:
  - formatting logic is needed
  - FX or localization is introduced

### Product identity (slug)

- `slug` must uniquely identify a sellable product (SKU)
- do not reuse the same slug for multiple variants

Examples:
- smartbudget-ru
- smartbudget-int

Reason:
- routing (/products/{slug})
- reviews (/reviews/{slug})
- clear separation between product variants

### Product deliverable (MVP)

- each product includes its own downloadable archive
- archive contains:
  - Excel file (SmartBudget)
  - PDF walkthrough

- archive is stored as a single file per product
- no separate file entities in MVP

Reason:
- simplifies implementation
- aligns with SKU-based product model
- avoids premature file versioning complexity

Future:
- allow multiple files and versioning (separate table)

## Sprint 14: Product pricing redesign (SKU + product_prices)

### Completed:

- removed `price` field from `products`
- introduced `product_prices` table:
  - `product_id`
  - `currency_code`
  - `amount`
  - `is_active`
  - `created_at`
- implemented data migration:
  - backfilled prices from `products.price`
  - preserved all existing price data

- introduced service layer logic:
  - `set_product_price`
  - deactivates previous active price
  - creates new active price
  - validates:
    - currency (RUB/EUR)
    - amount > 0
    - product existence

- added DB-level constraint:
  - partial unique index:
    - one active price per (product_id, currency_code)

- updated repository:
  - replaced direct `price` usage with join to `product_prices`
  - active price resolved in SQL (not in template)

- updated admin UI:
  - displays active price (amount + currency)
  - added `slug` column (SKU visibility)

- updated tests:
  - service tests for pricing logic:
    - create first price
    - replace active price
    - reject invalid currency
  - updated admin route test to use new pricing model

### Architecture decisions:

- product = sellable SKU (not abstract product)
- pricing is separated from product identity
- pricing is append-only (history preserved)
- business rules enforced in service layer
- critical invariants enforced at DB level (partial index)

### Result:

- flexible pricing model
- supports:
  - multiple currencies
  - price history
  - future USD extension without schema change

## Sprint 15: Admin product management + admin auth

### Completed:

#### Admin authentication

- implemented admin login (`/admin/login`)
- implemented logout (`/admin/logout`)
- introduced cookie-based auth (`admin_token`)
- moved auth logic to `app.dependencies.require_admin`
- applied protection via `admin_router` (router-level dependency)
- removed query-based token access (URL no longer exposes secrets)

#### Admin dashboard

- added `/admin` as entry point
- created `admin_dashboard.html`
- added navigation:
  - Products
  - Feedback
- unified UI with existing admin styles

#### Admin products (full flow)

- implemented create product:
  - Product + ProductPrice (separated)
- implemented edit product:
  - updates Product fields
  - replaces active ProductPrice if changed
- restored `/admin/products/new` (GET)
- ensured:
  - one active price per currency
  - no price stored in Product model

#### UI improvements

- styled:
  - product form
  - dashboard
  - login page
- introduced reusable admin form layout (`admin_products.css`)

#### Test updates

- migrated all tests to new pricing model:
  - removed `price` from Product
  - added `set_product_price`
- updated product status values (`in_sale` instead of `active`)
- added required `archive_path` in tests
- introduced helper `auth_client` for admin routes
- fixed all admin route tests (403 → authorized access)
- full test suite passing

### Architecture decisions:

- admin auth = simple cookie-based (no JWT)
- admin protection applied at router level (not per route)
- product creation MUST include initial price
- tests must always reflect real DB constraints

### Result:

- working admin panel (auth + navigation)
- correct product + pricing model
- stable test suite
- clean base for next steps (payments, sales, reviews UX)