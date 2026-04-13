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

## Next sprint priorities

### 1. Product model redesign

- product = sellable package (SKU)
- introduce:
  - SmartBudget RU
  - SmartBudget INT
- each product = its own downloadable archive:
  - Excel
  - PDF walkthrough

---

### 2. Product pricing architecture

- remove ambiguous `price`
- introduce currency-aware pricing

Initial:
- RU → RUB
- INT → EUR

Requirement:
- must support future USD without redesign

---

### 3. Admin product management

- redesign create/edit forms
- keep `/admin/products` as main screen
- implement Edit AFTER model redesign

---

### 4. Merchant of Record evaluation

- prefer MoR over custom checkout

Evaluate:
- Paddle
- Lemon Squeezy
- Stripe

---

### 5. Sales tracking (admin)

- sales list
- filtering
- purchase validation consistency

---

### 6. Reviews UX improvements

- show preview on landing
- optional rating later

---

### 7. Feedback tightening

- enforce `product_id`
- validate `sale_id ↔ product_id`

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