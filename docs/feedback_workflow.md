# Feedback Workflow

## Scope

This document describes ONLY:

- feedback lifecycle
- admin workflow
- publication rules
- business rules for feedback → review → Q&A

It does NOT describe:

- database schema
- backend layers
- repository/service architecture
- product/pricing models

For system architecture and data model, see:
- docs/backend_architecture.md

## Purpose

This document describes how feedback messages are handled in the admin UI and what business rules apply to each message type.

---

## Feedback message types

### 1. `site_issue`

**Purpose:**
- private support only
- should not be published publicly

**Expected handling:**
- admin reviews the message
- admin prepares a reply draft
- admin may send one email reply (if email is available)
- further communication continues in email client

**Publication rules:**
- must never be published as a public review

---

### 2. `general_question`

**Purpose:**
- private communication only
- should not be published publicly

**Expected handling:**
- admin reviews the message
- admin prepares a reply draft
- admin may send one email reply (if email is available)
- further communication continues in email client

**Publication rules:**
- must never be published as a public review

---

### 3. `product_feedback`

**Purpose:**
- product-related feedback
- may become a public review

**Expected handling:**
- admin reviews the message
- admin prepares a reply draft
- admin may send one email reply
- alternatively, admin may publish as public review

**Important:**
- once published → email sending is blocked

**Publication rules:**
- only `product_feedback` can be published
- requires non-empty `admin_reply`

When published:
- `is_published = true`
- `published_at` is set

When unpublished:
- `is_published = false`
- `published_at = null`

---

## Admin UI workflow

### List page

Shows:
- feedback id
- created_at
- type
- email
- subject
- resolved status

**Sorting:**
- unresolved first
- newest first inside groups

---

### Detail page

Allows admin to:
- view message
- mark resolved / open
- edit reply draft
- send email
- publish / unpublish review

---

## Reply Draft

`admin_reply` is an internal draft.

**Important:**
- not sent automatically
- editable anytime before sending
- required for publishing

---

## Email sending rules

Email is a **one-time action**.

**Requirements:**
- non-empty `admin_reply`
- non-empty `email`

**Restrictions:**
- cannot send more than once (`reply_sent_at`)
- cannot send if `is_published = true`

**After sending:**
- `reply_sent_at` is set
- `reply_sent_to_email` is stored
- дальнейшее общение вне админки

---

## Publication rules

Only `product_feedback` can be published.

**Rules:**
- publish button only for product feedback
- requires non-empty `admin_reply`
- blocked for other types

---

## Product-based reviews

Reviews are tied to specific product SKUs (sellable packages).

Important:
- each review belongs to a specific product variant (e.g. SmartBudget RU or SmartBudget INT)
- reviews are NOT shared between different product variants

**Requirements:**
- `type = product_feedback`
- `is_published = true`
- `product_id` is set

**Display:**
- `/reviews/{slug}` → per product
- `/reviews` → redirect

**Consistency:**
- `product_id` must match `sale_id` (if exists)
- feedback without `product_id` cannot be published

**Design decision:**
- no global reviews
- product-scoped from start

Important:
- reviews are tied to specific product SKUs (sellable packages)
- each review belongs to one specific product variant
- SmartBudget RU and SmartBudget INT must have separate reviews
- reviews are not shared across different product variants

---

## Design decision

Admin UI is **not an email client**.

- admin sends first reply
- дальнейшее общение → email
- no thread management in admin

---

## Next implementation priorities

### 1. Product model redesign

- product = SKU
- SmartBudget RU
- SmartBudget INT
- each = archive (Excel + PDF)

---

### 2. Product pricing architecture

- remove raw `price`
- introduce currency-aware model

Initial:
- RU → RUB
- INT → EUR

Future:
- USD without redesign

---

### 3. Merchant of Record

- evaluate MoR-first approach
- keep model provider-agnostic

---

### 4. Admin product management

- `/admin/products` = main UI
- implement Edit after redesign

---

### 5. Sales management

- sales list
- filtering
- validation

---

### 6. Reviews UX

- preview on landing
- improve UI

---

### 7. Feedback tightening

- require `product_id`
- validate `sale_id ↔ product_id`

---

## Product Q&A (`product_qna`)

**Purpose:**
- curated FAQ

**Source:**
- derived from feedback

**Workflow:**
1. user sends feedback
2. admin reviews
3. if useful:
   - rewrite question
   - write answer
4. publish as Q&A

**Difference:**
- Q&A = short answers
- articles = separate feature

---

## Test coverage status

### Covered:

- send email:
  - missing email
  - success
  - already sent
  - missing reply
  - published restriction

- publish:
  - invalid type
  - success
  - toggle
  - missing reply

- resolve toggle
- reply draft save
- empty normalization

---

### Routes:

- send email:
  - success
  - repeated send blocked

- publish:
  - publish/unpublish

---

### Test isolation:

- SMTP blocked
- mail mocked globally

---

### Architecture note:

- service tests → business logic
- route tests → wiring only

---

### Known limitation:

- mail sending not fully isolated everywhere yet

---

## Design clarification: feedback vs review vs Q&A

- **Feedback:**
  - raw input
  - private

- **Review:**
  - derived from feedback
  - public

- **Q&A:**
  - curated
  - rewritten

**Important:**
- feedback ≠ public content
- publication = transformation

---

## Future data model note

Current:
- `is_published` inside `feedback_messages`

This is a transitional solution.

Target architecture:

- feedback_messages:
  - private, raw user input
  - never used directly for public display

- product_reviews:
  - separate table
  - stores only approved and curated public reviews
  - linked to product_id

- product_qna:
  - separate table
  - curated Q&A content

Rationale:
- separation of concerns
- no mixing raw input with public content
- independent lifecycle for reviews and Q&A

---

## Related architecture

See:

- `docs/feedback_and_reviews_architecture.md`

Target:
- reviews separated from feedback
- feedback remains private channel