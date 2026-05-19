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

## Sprint 19: Purchase flow + checkout UI/CSS polish

### Completed:

* created dedicated `product_buy.css`
* redesigned `/products/{family_slug}/buy` into responsive product cards
* implemented responsive 2-column → 1-column layout
* improved:

  * spacing
  * typography
  * CTA hierarchy
  * card structure
* replaced inline JavaScript in templates with structured event-based logic
* added consultation checkbox UX improvements
* implemented localization-aware recommended product logic:

  * RU interface → RU package recommended
  * EN interface → INT package recommended
* fixed language propagation issue on `product_buy`

  * added `lang` to template context
* updated language switch UX:

  * navigation now displays current language instead of target language
* improved mobile/tablet responsiveness for:

  * product cards
  * hero typography
  * CTA buttons
  * checkout summary block
  * payment buttons
* added adaptive breakpoints for:

  * tablets
  * large phones
  * compact phones
* stabilized product card height alignment for 2-column layouts
* improved ultra-mobile behavior (~320px width)
* aligned checkout visual style with product-buy page

### Architecture / UX decisions:

* avoid inline JavaScript in templates where possible
* UI language and recommended package are related UX concepts
* mobile-first responsive polish is required even for MVP purchase flow
* compact/mobile layouts should prefer readability over strict two-column preservation
* checkout and product-buy pages should share a unified visual style

---

## Sprint 20 checkpoint: consultation flow architecture clarified

### Context restored

During Sprint 20 planning, the logical connection between the purchase flow, consultation flow, and future sales architecture was clarified.

The current product flow is:

* `/products` — public product catalog
* `/products/smartbudget` — SmartBudget landing page
* `/products/smartbudget/buy` — SmartBudget SKU/package selection page
* `/checkout/{product_slug}` — checkout page for the selected SKU

The landing page should remain a product explanation page, not a price list.
Product prices belong on the buy/selection page, because SmartBudget may have multiple SKUs:

* RU Standard
* INT Standard
* RU Pro later
* INT Pro later
* possible future editions/packages

### Final UX decision

SmartBudget landing page must provide two separate user paths:

1. Buy SmartBudget

   * user goes to `/products/smartbudget/buy`
   * selects exact SKU/package/version
   * may optionally add a setup consultation
   * add-on consultation price must be visible before checkout
   * checkout confirms product price, consultation price, and total

2. Book standalone consultation

   * user goes to a separate consultation page
   * user sees standalone consultation price and terms
   * user pays for consultation
   * Calendly booking is shown only after successful payment

### Important UX rule

Consultation price must never appear for the first time only on checkout.

The discounted consultation add-on price must be visible on the buy page next to the checkbox, for example:

* `Add 1:1 SmartBudget setup consultation + 35 EUR`
* `Добавить личную консультацию по настройке SmartBudget + 3 500 RUB`

Checkout should only confirm the selected items and total amount.

### Calendly decision

Calendly must be available only after successful payment.

Reason:

* do not allow unpaid booking of limited consultation slots
* keep consultation capacity protected
* avoid manual cleanup of unpaid bookings

---

### Consultation notification flow note

Consultation flow has two separate business events:

1. consultation purchased
2. consultation slot booked in Calendly

These events must not be treated as the same thing.

Example:

* customer may purchase consultation
* but postpone Calendly booking
* or never complete booking

Purchased consultation does not automatically mean booked consultation.

For MVP:

* booking responsibility belongs to the customer
* customer receives booking access immediately after payment
* consultation may remain unused if no slot is selected

### Calendly access flow

After successful payment:

* user is redirected to success page
* success page contains Calendly booking button/link
* purchase confirmation email also contains the same Calendly link

Reason:

* user may close browser without booking immediately
* confirmation email acts as fallback access to booking flow

### Important MVP rule

Calendly link should not be generated later manually.

The same booking link should be:

* shown immediately after payment
* included in confirmation email

### Calendly single-use booking link rule

Consultation booking must use a single-use Calendly link, not a public reusable booking link.

Reason:

* each paid consultation item gives access to exactly one booking slot
* discounted add-on consultation must not allow repeated bookings
* standalone consultation must also allow only one booking per paid consultation item

MVP rule:

* after successful payment, customer receives one single-use Calendly link
* the same single-use link is shown on success page
* the same single-use link is included in purchase confirmation email
* after one successful Calendly booking, the link expires and cannot be reused

This applies to both:

* SmartBudget consultation add-on
* standalone consultation purchase

Future implementation note:

* generate/store one Calendly single-use link per paid consultation sale item
* store it on the sale item or future consultation booking record
* later use Calendly webhook to store scheduled/completed booking status

### Calendly link separation rule

Add-on consultation and standalone consultation must use separate booking links.

Reason:

* add-on consultation has discounted price
* standalone consultation has higher standalone price
* public users must not access discounted add-on booking flow without buying SmartBudget

MVP rule:

* add-on Calendly link is shown only after successful SmartBudget purchase with consultation add-on
* standalone Calendly link is shown only after successful standalone consultation purchase
* SmartBudget landing page must not expose add-on Calendly link directly

### MVP approach

For MVP:

* rely on native Calendly email notifications
* admin receives booking email immediately after user selects a slot

This avoids premature webhook/integration complexity.

### Future architecture direction

Later implement:

Calendly webhook
→ backend endpoint
→ consultation booking record
→ Telegram notification

Possible future endpoint:

`/v1/webhooks/calendly`

Possible future Telegram notification example:

```text
New consultation booked:
Client: ...
Package: SmartBudget INT
Consultation type: add-on
Time: ...
Calendly booking URL: ...
```

### Important business rule

`admin_sales` and consultation scheduling are different concerns.

`admin_sales` tracks:

* purchases/payments

Calendly tracks:

* actual booked consultation slots

## Consultation architecture design note

### Current state

`ServiceAddon` already exists and is used by checkout.

Current fields include:

* `code`
* `name`
* `service_type`
* `family_slug`
* `package_code`
* `currency_code`
* `amount`
* `is_active`

Current repository lookup uses:

* `family_slug`
* `package_code`
* `service_type`

This is no longer sufficient because the same service type can be sold in different usage scenarios.

Example:

* consultation as discounted SmartBudget add-on
* consultation as standalone service with higher standalone price

### Decision

Add `usage_type` to `service_addons`.

Allowed MVP values:

* `addon`
* `standalone`

Example records:

* `consultation_1h_ru_addon`
  * `service_type = consultation`
  * `usage_type = addon`
  * `family_slug = smartbudget`
  * `package_code = RU`
  * `currency_code = RUB`
  * `discounted add-on price`

* `consultation_1h_ru_standalone`
  * `service_type = consultation`
  * `usage_type = standalone`
  * `family_slug = smartbudget`
  * `package_code = RU`
  * `currency_code = RUB`
  * `standalone consultation price`

* `consultation_1h_int_addon`
  * `service_type = consultation`
  * `usage_type = addon`
  * `family_slug = smartbudget`
  * `package_code = INT`
  * `currency_code = EUR`
  * `discounted add-on price`

* `consultation_1h_int_standalone`
  * `service_type = consultation`
  * `usage_type = standalone`
  * `family_slug = smartbudget`
  * `package_code = INT`
  * `currency_code = EUR`
  * `standalone consultation price`

### Why not use `addon_price` / `standalone_price` fields

Do not add separate price columns such as:

* `addon_price`
* `standalone_price`

Reason:

* this makes the table harder to extend
* each usage scenario should be an explicit offer/record
* future services may have more than two usage scenarios
* admin UI stays simpler when each row has exactly one price

### Repository rule

`ServiceAddonRepository.get_active_addon()` must be extended to filter by:

* `family_slug`
* `package_code`
* `service_type`
* `usage_type`

For SmartBudget checkout add-on usage:

* `service_type = consultation`
* `usage_type = addon`

For standalone consultation page:

* `service_type = consultation`
* `usage_type = standalone`

---

## Sprint 22 checkpoint: consultation usage_type stabilization

### Completed:

* added `usage_type` to `ServiceAddon`
* implemented DB migration with safe backfill strategy
* existing consultation add-ons are now migrated to:

  * `usage_type = addon`
* updated `ServiceAddonRepository.get_active_addon()` lookup:

  * `family_slug`
  * `package_code`
  * `service_type`
  * `usage_type`
* updated checkout route:

  * consultation in checkout is now explicitly resolved as:

    * `service_type = consultation`
    * `usage_type = addon`
* updated `/products/{family_slug}/buy` backend context:

  * route now builds `product_options`
  * each product card receives:

    * product
    * active product price
    * consultation add-on
* updated `product_buy.html`:

  * consultation special price is now visible before checkout
  * add-on price is shown directly inside product cards
  * unavailable add-ons are handled safely
* improved consultation add-on UX:

  * introduced "Special price with purchase" messaging
  * stabilized responsive behavior for consultation pricing block
  * protected monetary amount from bad line wrapping
* added/updated tests:

  * model tests
  * repository tests
  * checkout tests
* added regression coverage:

  * checkout must ignore `usage_type = standalone`
  * checkout must use only `usage_type = addon`

### Architecture decisions:

* `service_type` defines WHAT the service is:

  * consultation
  * onboarding
  * support

* `usage_type` defines HOW the service is sold:

  * addon
  * standalone

* checkout product flow must never implicitly load standalone consultation pricing
* consultation pricing must be visible before checkout begins
* `ProductsRepository` remains product-focused and does not resolve service/add-on logic

---

## Sprint 23: sale_items architecture foundation

### Problem with current architecture

Current sales architecture assumes:

* one sale = one product

This is no longer correct.

Examples:

* SmartBudget + consultation add-on
* standalone consultation purchase
* future multiple services/add-ons
* future bundles or multiple quantities

Current architecture cannot correctly represent:

* multiple purchased items
* item-level pricing
* item-level service tracking
* item-level Calendly links
* item-level webhook processing

This becomes especially important for:

* Paddle webhooks
* consultation fulfillment
* standalone services
* future refunds/partial refunds

---

## Target architecture

### `sales` = order header

`sales` should become an order-level entity.

Responsibilities:

* customer identity
* payment status
* provider transaction IDs
* total amount
* currency
* timestamps
* payment provider metadata

Example:

```text
Sale #1001
Customer: user@example.com
Currency: EUR
Total: 74 EUR
Status: paid
```

`sales` should NOT directly represent purchased business items anymore.

---

### New table: `sale_items`

Each purchased item must become a separate row.

Example:

```text
Sale #1001
 ├── SmartBudget INT Standard
 └── Consultation add-on
```

---

## Initial MVP item types

Allowed item types:

* `product`
* `service`

### Product item examples

* SmartBudget RU Standard
* SmartBudget INT Standard
* future Pro editions

### Service item examples

* consultation add-on
* standalone consultation
* future onboarding/support services

---

## Planned `sale_items` responsibilities

Each sale item should eventually support:

* independent pricing snapshot
* independent fulfillment state
* independent webhook linkage
* independent external metadata
* independent refundability

This is especially important for services.

Example:

* product may already be delivered
* consultation may still be unbooked

These are different lifecycle states.

---

## Important architecture rule

`products` and `service_addons` remain catalog/configuration entities.

`sale_items` are immutable purchase snapshots.

Reason:

Catalog pricing may change later.
Purchase history must remain historically accurate.

Example:

```text
Current consultation price:
79 EUR

Old sale item:
35 EUR
```

Sale item must preserve the historical purchased price.

---

## Future consultation flow implication

Calendly access should eventually belong to a specific `sale_item`, not to the entire sale.

Reason:

One order may later contain:

* multiple consultations
* multiple services
* future recurring services

Correct ownership level is:

```text
sale_item
```

not:

```text
sale
```

---

## Future Paddle webhook implication

Paddle webhook events should eventually resolve:

```text
provider transaction
→ sale
→ sale_items
```

instead of:

```text
provider transaction
→ product only
```

This architecture is required for:

* mixed carts
* add-ons
* standalone services
* future refunds
* future subscription-like services

---

## Migration strategy note

Do NOT immediately delete old `sales.product_id` logic.

Recommended migration approach:

1. introduce `sale_items`
2. backfill existing sales
3. temporarily support both architectures
4. migrate business logic gradually
5. remove old direct product linkage later

Reason:

This reduces migration risk and keeps rollback simpler.

---

## Consultation booking ownership model

### Architectural decision

Calendly is used only as:

* scheduling UI
* slot management provider
* calendar integration layer

Critical business rules MUST remain under SmartBudgetSite backend control.

The system MUST NOT rely on Calendly one-time links as the primary protection mechanism.

Reason:

* avoid vendor lock-in
* avoid dependency on Calendly pricing/features
* maintain full control over entitlement logic
* support future migration to another booking provider or custom scheduler

---

## Consultation entitlement flow

After successful purchase:

* backend creates consultation entitlement record
* generates secure UUID booking token
* sets expiration timestamp (currently: 14 days)

Example:

* status = "available"
* expires_at = now + 14 days

User receives a booking link similar to:

```text
/consultation/book/{token}
```

---

## Backend responsibilities

Before showing Calendly embed/page:

* validate token existence
* validate token is not expired
* validate token is not already used
* validate purchase entitlement exists

If validation fails:

* booking page must not be accessible
* user should see explanatory error message

---

## Booking finalization

Calendly webhook is used only to:

* confirm successful booking
* save Calendly event reference
* mark consultation entitlement as used/booked

Example status flow:

* available
* booked
* expired
* cancelled (future)

After successful booking:

* token becomes unusable
* repeated booking attempts must be blocked by backend

---

## Important business rule

Discounted add-on consultations purchased together with SmartBudget:

* are single-use
* are non-repeatable
* must not allow multiple bookings from the same entitlement

The backend must enforce this rule independently from Calendly capabilities.

---

## Future flexibility

This architecture intentionally separates:

* business ownership (SmartBudgetSite)
* scheduling provider (Calendly)

This allows future replacement of Calendly without rewriting consultation entitlement logic.

---

## Sprint 23 checkpoint: sale_items architecture foundation

### Completed:

* introduced `sale_items` table
* added `SaleItem` model
* implemented item-level constraints:

  * exactly one ownership reference
  * product/service type validation
  * positive quantity
  * non-negative amount
* added `Sale.items` relationship
* introduced itemized order architecture:

  * `Sale` = order header
  * `SaleItem` = purchased business entity
* implemented service-layer purchase creation helpers:

  * `create_product_sale`
  * `create_service_sale_item`
  * `create_standalone_service_sale`
* implemented:

  * standalone service sales
  * service-only sales
  * item-level pricing snapshots
* added:

  * `calculate_sale_total()`
* migrated `/v1/check-purchase` logic:

  * product ownership now resolved through `sale_items`
  * no longer depends on `sales.product_id`
* converted previous `xfail` service-only verification test into passing regression coverage
* introduced centralized constants:

  * `SaleItemType.PRODUCT`
  * `SaleItemType.SERVICE`
* added extensive model/service/repository regression coverage

### Transitional architecture state

`sales.product_id` still exists temporarily as a legacy compatibility field.

Current architecture:

```text
Sale
    ↓
SaleItems
    ├── Product item
    └── Service item
```

`SaleItem` is now the source of truth for purchase ownership.

### Important migration decision

Legacy `sales.product_id` must NOT be used for new business logic.

New code should resolve ownership through:

```text
Sale → SaleItems
```

The legacy field is kept only to support:

* incremental migration
* rollback safety
* compatibility with older flows/tests/admin logic

Future cleanup should eventually:

* fully remove `sales.product_id`
* fully derive totals from `sale_items`
* move all purchase logic to item-based ownership

---

## Sprint 24: consultation entitlement system design

### Core architecture decision

Consultation access must be represented by a backend-owned entitlement entity.

The entitlement is the source of truth for whether a customer may access the booking flow.

Calendly must not be treated as the owner of consultation access rights.

Correct ownership chain:

```text
Sale
  ↓
SaleItem
  ↓
ConsultationEntitlement
```

Incorrect ownership chain:

```text
Sale
  ↓
Calendly booking
```

Reason:

* a consultation can be purchased but not booked immediately
* an entitlement can expire without any Calendly event
* Calendly can be replaced later by another provider
* booking provider rules must not define SmartBudget business rules
* discounted add-on consultations must remain single-use even if provider-side links are reusable or misconfigured

---

### ConsultationEntitlement responsibility

`ConsultationEntitlement` represents customer access to one consultation booking right.

It is responsible for:

* linking consultation access to a specific purchased `SaleItem`
* storing backend-owned secure booking token
* storing token expiration timestamp
* storing current entitlement status
* blocking repeated booking attempts
* acting as the stable business object for future Calendly webhook processing

It is NOT responsible for:

* storing product catalog pricing
* replacing `SaleItem` as purchase snapshot
* acting as a generic sale/order entity
* rendering Calendly UI
* defining provider-specific webhook payload structure

---

### Relationship rules

MVP relationship:

```text
SaleItem (service/consultation) 1 → 0..1 ConsultationEntitlement
```

MVP rule:

* only paid consultation service items should receive an entitlement
* product-only sale items must not receive an entitlement
* entitlement belongs to `sale_item_id`, not directly to `sale_id`

Reason:

* consultation ownership exists at item level
* future orders may contain multiple service items
* future refunds or cancellations may affect one item without affecting the whole sale

Future-compatible direction:

```text
SaleItem (service/consultation) 1 → many ConsultationEntitlements
```

This may be useful later for:

* multi-session consultation packages
* onboarding bundles
* support packages

MVP should still implement one entitlement per consultation sale item unless requirements change.

---

### Booking token rules

Each entitlement receives a backend-generated UUID token.

Example public booking URL:

```text
/consultation/book/{token}
```

Token validation must happen before Calendly access is shown.

Validation rules:

* token exists
* entitlement status allows booking
* entitlement is not expired
* linked sale item exists
* linked sale/payment is valid for booking access

If validation fails:

* Calendly must not be shown
* user should see a clear explanatory page

Token must be single-use from the SmartBudget backend perspective.

Calendly one-time links may be used as an implementation detail later, but backend validation remains mandatory.

---

### Entitlement lifecycle

MVP statuses:

* `available`
* `booked`
* `expired`
* `cancelled`

Initial status after successful payment:

```text
available
```

Expected lifecycle:

```text
available → booked
available → expired
available → cancelled
booked → cancelled   (future/manual/admin scenario)
```

Status meaning:

* `available` — customer may access booking page if token is valid and not expired
* `booked` — consultation slot was successfully booked; token must no longer allow booking
* `expired` — booking window passed without successful booking
* `cancelled` — entitlement was manually or automatically cancelled; future behavior may depend on business rules

MVP rule:

* expired status may be derived dynamically from `expires_at`
* physical status update can be implemented later by scheduled job or admin action

---

### Expiration rule

Default MVP booking window:

```text
expires_at = created_at + 14 days
```

Business meaning:

* customer has 14 days after purchase to book a consultation slot
* after expiration, booking access is blocked

Important:

Expiration controls access to booking, not necessarily the consultation event date.

Example:

* customer buys consultation on May 1
* books a slot on May 10
* slot itself may happen on May 20
* this is valid because booking happened before entitlement expiration

---

### Calendly integration boundary

Calendly should be integrated after entitlement validation.

The booking page flow should be:

```text
User opens /consultation/book/{token}
  ↓
Backend validates entitlement
  ↓
If valid: show Calendly embed/link
  ↓
Calendly booking happens
  ↓
Calendly webhook confirms booking
  ↓
Backend marks entitlement as booked
```

Calendly webhook must not create entitlement.

Webhook should only update an existing entitlement that was already created after successful payment.

---

### Future webhook fields

The entitlement model should leave room for provider metadata, for example:

* booking_provider
* provider_event_uri
* provider_invitee_uri
* booked_at
* cancelled_at

Do not overbuild webhook handling in MVP.

First implementation should focus on:

* model/table
* token generation
* entitlement creation after consultation purchase
* token validation service

---

## Sprint 25 checkpoint: consultation booking lifecycle foundation

### Completed:

* implemented lifecycle transition service:

  * `mark_entitlement_as_booked()`
* implemented BOOKED transition rules:

  * only AVAILABLE entitlements may transition to BOOKED
  * BOOKED transition is idempotent
* added booking metadata fields to `ConsultationEntitlement`:

  * `booking_provider`
  * `provider_event_uri`
  * `provider_invitee_uri`
  * `booked_at`
* implemented provider booking metadata persistence
* added lifecycle regression coverage:

  * BOOKED happy path
  * idempotent repeated booking confirmation
  * EXPIRED entitlement rejection
  * CANCELLED entitlement rejection
* introduced reusable test helper:

  * `create_test_consultation_entitlement()`
* implemented provider reconciliation repository:

  * `ConsultationEntitlementRepository`
  * `get_by_provider_event_uri()`
* added repository regression coverage:

  * matching provider event lookup
  * unknown provider event returns None
* added unique partial index:

  * `uq_consultation_entitlements_provider_event_uri`
* enforced external reconciliation integrity:

```text
one provider event
    ↓
exactly one entitlement
```

### Architecture decisions:

* lifecycle transitions belong to service layer, not repositories
* booking confirmation must remain idempotent because webhook providers retry delivery
* provider metadata persistence is optional before booking and populated only after successful booking confirmation
* repository layer is responsible only for reconciliation lookup, not lifecycle decisions
* `provider_event_uri` acts as external reconciliation key
* partial unique index is required because NULL provider event URIs are valid before booking
* tests should validate business behavior rather than internal helper implementation details

### Current lifecycle state

```text
AVAILABLE
    ↓
BOOKED
```

Supported behaviors:

* AVAILABLE → BOOKED
* BOOKED → BOOKED (safe idempotent noop)
* EXPIRED → BOOKED (blocked)
* CANCELLED → BOOKED (blocked)

### Current webhook readiness state

The backend is now capable of:

```text
provider event
    ↓
repository reconciliation lookup
    ↓
entitlement resolution
    ↓
idempotent booking confirmation
```

### Current limitation

* webhook endpoint not implemented yet
* provider signature verification not implemented yet
* Calendly payload normalization layer not implemented yet
* booking cancellation synchronization not implemented yet

---

## Sprint 24 checkpoint: consultation entitlement MVP foundation

### Completed:

* added `ConsultationEntitlement` model
* added Alembic migration for `consultation_entitlements`
* implemented entitlement statuses:

  * `available`
  * `booked`
  * `expired`
  * `cancelled`
* added secure UUID booking token generation
* implemented relationship chain:

```text
Sale
  ↓
SaleItem
  ↓
ConsultationEntitlement
```

* implemented service-layer entitlement creation:

  * `create_consultation_entitlement()`
* implemented token validation service:

  * `get_valid_consultation_entitlement_by_token()`
* implemented protected booking route:

  * `/consultation/book/{booking_token}`
* added placeholder booking page:

  * `consultation_booking.html`
* implemented backend-controlled entitlement validation before booking access
* added timezone normalization helper:

  * `_ensure_utc_aware()`
* stabilized SQLite/PostgreSQL datetime comparison behavior
* implemented extensive regression coverage:

  * entitlement creation happy path
  * reject product sale items
  * reject duplicate entitlement creation
  * valid token lookup
  * unknown token rejection
  * expired token rejection
  * booking route access with valid token

### Architecture decisions:

* entitlement creation belongs to service layer, not ORM model defaults
* low-level services use `flush()` instead of `commit()`
* transaction boundaries remain controlled by higher-level orchestration flow
* booking routes remain thin and delegate validation to service layer
* Calendly integration remains postponed until entitlement foundation is stable
* backend entitlement validation is mandatory even if Calendly later supports one-time booking links

### Current booking flow

```text
Purchase successful
  ↓
Create ConsultationEntitlement
  ↓
User opens:
/consultation/book/{token}
  ↓
Backend validates entitlement
  ↓
If valid → booking UI/provider access allowed
```

### Current limitation

* Calendly embed/webhook integration not implemented yet
* booked/cancelled status transitions still pending
* booking confirmation lifecycle not implemented yet

---

## Sprint 25: consultation booking lifecycle foundation

### Architectural direction

Sprint 25 begins transition from:

```text
entitlement validation only
```

into:

```text
full consultation booking lifecycle
```

The system must now support:

* successful booking confirmation
* irreversible booking ownership transition
* provider metadata persistence
* repeated booking prevention
* future webhook-driven synchronization

---

### Core lifecycle rule

`ConsultationEntitlement` remains the backend-owned source of truth.

Booking providers (Calendly initially) may confirm bookings,
but they must not define whether the consultation is considered booked.

Correct authority:

```text
ConsultationEntitlement.status
```

not:

```text
provider booking existence
```

Reason:

* provider webhook delivery may fail
* provider events may later be deleted/cancelled
* providers may be replaced
* business ownership must remain internal

---

### Booked transition rule

A consultation becomes booked only after backend confirmation.

Expected future flow:

```text
available entitlement
  ↓
customer books slot in Calendly
  ↓
Calendly webhook received
  ↓
backend validates webhook
  ↓
backend updates entitlement
  ↓
status = booked
```

After successful transition to `booked`:

* booking token becomes unusable
* booking page access must be blocked
* repeated booking attempts must fail

---

### Planned booking metadata

`ConsultationEntitlement` should support provider-related metadata.

Planned MVP-compatible fields:

* `booking_provider`
* `provider_event_uri`
* `provider_invitee_uri`
* `booked_at`

Purpose:

* connect backend entitlement to provider booking
* support future admin visibility
* support debugging/webhook reconciliation
* support future cancellation flows

Important:

Provider metadata must remain optional.

Reason:

* entitlement may exist before booking
* webhook may fail temporarily
* provider integration should not block entitlement creation

---

### Important transition rule

Booking confirmation logic must be idempotent.

Example:

If Calendly retries the same webhook multiple times:

* backend must not create duplicate transitions
* backend must not raise inconsistent state errors
* backend should safely ignore already-booked entitlements

This is especially important because webhook providers commonly retry delivery.

---

### Important architecture boundary

Webhook handlers should remain thin.

Recommended flow:

```text
Webhook route
  ↓
Webhook service
  ↓
Consultation entitlement service
  ↓
Repository/DB
```

Webhook route responsibilities:

* validate provider signature
* parse payload
* call service

Business rules must remain inside services.

---

### Sprint 25 implementation priorities

1. booked status transition service
2. booking confirmation persistence
3. repeated booking prevention
4. provider metadata model design
5. webhook-ready service boundary

---

## Next sprint priorities (after Sprint 25)

### 1. Webhook integration boundary

* design Calendly webhook integration layer
* implement webhook route structure
* define webhook service orchestration
* implement provider payload normalization
* prepare signature verification abstraction
* implement reconciliation flow:

```text
provider webhook
    ↓
provider payload normalization
    ↓
repository lookup
    ↓
entitlement resolution
    ↓
idempotent lifecycle transition
```

### 2. Calendly integration layer

* add Calendly embed/button after successful entitlement validation
* define provider abstraction boundary
* prepare webhook endpoint structure

### 3. Merchant of Record integration (Paddle)

* create Paddle account
* configure products and prices
* implement checkout redirect
* define success URL
* plan webhook handling

### 4. Sales tracking (admin)

* sales list
* filtering
* show consultation presence

### 5. Reviews UX improvements

* show preview on landing
* optional rating later

### 6. Feedback tightening

* enforce `product_id`
* validate `sale_id ↔ product_id`

### 7. Deployment preparation

* connect domain
* choose hosting (VPS / PaaS)
* prepare environment variables
* basic production setup

### 1. Consultation booking lifecycle

* implement booked status transition
* design Calendly webhook update flow
* persist booking confirmation metadata
* prevent repeated booking after successful booking confirmation

### 2. Calendly integration layer

* add Calendly embed/button after successful entitlement validation
* define provider abstraction boundary
* prepare webhook endpoint structure

### 3. Merchant of Record integration (Paddle)

* create Paddle account
* configure products and prices
* implement checkout redirect
* define success URL
* plan webhook handling

### 4. Sales tracking (admin)

* sales list
* filtering
* show consultation presence

### 5. Reviews UX improvements

* show preview on landing
* optional rating later

### 6. Feedback tightening

* enforce `product_id`
* validate `sale_id ↔ product_id`

### 7. Deployment preparation

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