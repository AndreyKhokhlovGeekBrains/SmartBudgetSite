Paste your current .md file here and we will update it for the next sprint.

````
## How to resume work

When continuing development in a new session:

1. Start by reviewing:

   * docs/backend_architecture.md
   * docs/feedback_workflow.md

2. Focus on:

   * "Sprint checkpoint" section (current state)
   * "Next sprint priorities" section

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

* Render HTML pages (Jinja templates)
* Handle browser-based interactions
* Return `TemplateResponse` or `RedirectResponse`

Examples:

* `/feedback`
* `/admin/feedback`
* `/admin/feedback/{id}/send-email`
* `/admin/products`

---

### 2. API layer (`app/api/v1`)

Purpose:

* Provide JSON endpoints
* Used by frontend or external clients
* Return structured data (Pydantic models)

Examples:

* `/v1/check-purchase`
* `/v1/feedback`

---

### 3. Service layer (`app/services`)

Purpose:

* Contain business logic
* Independent from HTTP (no Request/Response)
* Reusable across Web and API

Examples:

* `send_feedback_reply`
* `toggle_feedback_publish`

Rules:

* Services may raise `HTTPException`
* Services operate on database models
* Services should not render templates

---

### 4. Repository layer (`app/repositories`)

Purpose:

* Encapsulate database access
* Provide reusable DB queries

Examples:

* `FeedbackAdminRepository`
* `ProductsRepository`

---

### 5. Core layer (`app/core`)

Purpose:

* Infrastructure
* Database engine, session
* Config, logging, i18n

---

### 6. Dependencies (`app/dependencies`)

Purpose:

* Dependency Injection (DI)
* Provide shared dependencies (e.g. DB session)

Important rule:

* Use `get_db` from this module everywhere
* Do not duplicate dependency functions

---

## Request flow

Typical flow:

Web route → Service → Repository → DB

or

API route → Service → Repository → DB

---

## Design principles

* Keep routes thin (no business logic)
* Move logic to services
* Avoid duplication
* Use a single DI entry point
* Keep layers independent

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

* call service
* return `TemplateResponse` or `RedirectResponse`

API route:

* call service
* return JSON

---

### 3. Use repository inside service

* do not access DB directly from routes
* use repository methods for queries

---

### 4. Add tests

Prefer testing services:

* test business logic directly
* verify DB changes
* verify exceptions (status_code, detail)

Optionally:

* add route tests for critical endpoints

---

## What NOT to do

Avoid:

* putting business logic in routes
* duplicating logic across routes
* creating multiple `get_db` implementations
* mixing HTML rendering with business rules

---

## Refactoring rule

If a route starts to contain:

* multiple `if` conditions
* validation logic
* DB updates

→ move this logic to a service

---

## Sprint checkpoint: admin feedback refactoring and tests

### Completed:

* unified `get_db` usage via `app.dependencies`

* removed duplicate DB dependency definitions

* made `feedback_messages.email` nullable

* added Alembic migration

* introduced service layer

* moved all feedback logic to `feedback_service`

* isolated email sending in `mail_service`

* added full service test coverage:

  * email sending rules
  * publish/unpublish
  * resolve toggle
  * reply draft
  * validation edge cases

* added route-level tests for critical flows

* implemented real SMTP sending (Gmail App Password)

* ensured:

  * clean separation of concerns
  * no real emails in tests (global mocking)

### Architecture decision:

* service tests = business logic
* route tests = wiring only

---

## Sprint 12: current admin products state

### Implemented:

* `ProductsRepository`
* route `/admin/products`
* route `/admin/products/new` (GET)
* template `admin_products_list.html`
* template `admin_product_form.html`
* basic route test for `/admin/products`
* list page is styled and acts as central admin UI

### Current limitations:

* Edit flow is not implemented
* Create form is temporary
* POST create must NOT be finalized yet
* product model still reflects old pricing logic

---

## Sprint checkpoint: product-based reviews

### Completed:

* added `product_id` to feedback
* created FK and migration
* backfilled existing data
* implemented product-scoped reviews
* added `/reviews/{slug}`
* redirect `/reviews → /reviews/smartbudget`
* updated repository, routes, tests

### Architecture decisions:

* reviews are product-scoped
* use `product_id` (not slug) internally
* reviews are scoped per product SKU (e.g. SmartBudget RU vs SmartBudget INT are independent)

---

## Sprint 17: Product family purchase flow

### Completed:

* added `family_slug` to products
* implemented product-family purchase options route:

  * `/products/{family_slug}/buy`
* linked SmartBudget landing CTA to:

  * `/products/smartbudget/buy`
* added repository method:

  * `ProductsRepository.list_products_by_family_slug`
* purchase options page now:

  * loads only products from the selected `family_slug`
  * shows only products with status `in_sale`
  * displays active product price from `product_prices`
  * links selected SKU to `/checkout/{product_slug}`
* checkout route now accepts optional consultation query flag:

  * `/checkout/{product_slug}?consultation=1`
* added shared helper:

  * `app/utils/product_utils.py`
  * `get_product_package(slug)`
* package display (`RU` / `INT`) is now derived from selected product SKU, not from UI language
* tests updated and passing:

  * repository coverage for product-family filtering
  * repository coverage for active price loading

### Architecture decisions:

* `family_slug` groups related SKUs under one product family
* `slug` still identifies one exact sellable SKU
* `/products/{family_slug}/buy` is the correct bridge between landing and checkout
* UI language and product package are separate concepts
* product package must be derived from selected product identity, not from current site language

### Current limitation:

* consultation can be selected in UI and passed to checkout as a query parameter
* checkout can display that consultation was selected
* consultation price is not yet calculated from the database
* total amount still reflects product price only until service/add-on pricing is implemented

---

## Sprint 18: Services/add-ons + checkout total + localization

### Completed:

* introduced `service_addons` model
* added fields:

  * `family_slug`
  * `package_code`
  * `service_type`
* seeded consultation add-ons:

  * RU (RUB)
  * INT (EUR)
* implemented `ServiceAddonRepository`
* integrated add-on into checkout route
* implemented total calculation:

  * product + optional consultation
* added currency mismatch guard in checkout
* implemented Jinja `money` filter

  * RU: `7 400,00`
  * EN: `7,400.00`
* passed `lang` from request to templates
* applied localization-aware formatting in UI
* updated checkout template:

  * separate product price
  * separate consultation price
  * correct total
* added tests:

  * checkout with add-on
  * currency mismatch guard
* seeded INT Standard product via migration
* improved buy page UX:

  * added RU/INT explanation (language + payment)
  * introduced recommended badge (INT)

### Architecture decisions:

* services/add-ons are separate from products
* pricing always comes from DB, never from UI/query params
* UI language and product package remain independent
* formatting is handled in templates, not backend
* currency mixing is explicitly forbidden at runtime

---

## Next sprint priorities (after Sprint 18)

### 1. Purchase flow UI polish (CSS focus)

* add dedicated CSS for `product_buy.html`
* convert product list into clean card layout
* visually distinguish RU vs INT

  * badge
  * subtle color difference
* highlight recommended option (INT)
* improve spacing, typography, hierarchy
* improve checkbox UX for consultation

### 2. Checkout UI polish

* improve summary block styling
* emphasize total amount
* improve visual hierarchy of product vs add-on
* align with premium SaaS checkout patterns

### 3. Sales migration to sale_items

* keep `sales` as order header
* introduce `sale_items`
* support:

  * product
  * service (consultation)
* enable xfailed service-only verification test

### 4. Merchant of Record integration (Paddle)

* create Paddle account
* configure products and prices
* implement checkout redirect
* define success URL
* plan webhook handling

### 5. Sales tracking (admin)

* sales list
* filtering
* show consultation presence

### 6. Reviews UX improvements

* show preview on landing
* optional rating later

### 7. Feedback tightening

* enforce `product_id`
* validate `sale_id ↔ product_id`

### 8. Deployment preparation

* connect domain
* choose hosting (VPS / PaaS)
* prepare environment variables
* basic production setup

---

## Product categorical fields design note

Use string + allowed sets:

* edition: {"Standard", "Pro"}
* status: {"in_sale", "in_development", "discontinued"}

### Reason:

* simple
* no migrations
* controlled via UI

---

## Admin UI access design note

### Current:

* admin authentication implemented via cookie-based token (`admin_token`)
* admin routes are protected using `require_admin` dependency at router level
* admin routes are not exposed via public navigation

### Rule:

* admin access must always require authentication
* admin links must not be visible to public users

### Future:

* consider role-based access if multiple admins are introduced
* optional: replace token with more robust auth if needed

---

## Product family / purchase options note

Current `products` table represents sellable SKUs.

Examples:

* smartbudget-ru-standard
* smartbudget-ru-pro
* smartbudget-int-standard
* smartbudget-int-pro

For purchase option pages, products must be grouped by product family.

Example flow:

* landing page: `/products/smartbudget`
* purchase options page: `/products/smartbudget/buy`
* checkout page: `/checkout/{product_slug}`

Important:
The purchase options page must NOT show all products from the `products` table.
It should show only SKUs that belong to the selected product family.

Reason:
In the future, the site may sell other products, such as:

* books
* templates
* consultations
* other digital products

Possible implementation options:

* add `family_slug` to `products`
* or introduce a separate `product_families` table

MVP direction:
Use `family_slug` on `products` first, because it is simple and enough for grouping SKUs.
A separate `product_families` table can be introduced later if product-family metadata becomes necessary.

### Important:

* SmartBudget RU and SmartBudget INT = separate SKUs
* each has:

  * its own archive
  * its own lifecycle

### Implication:

* product = sellable package, not abstract concept

---

````
