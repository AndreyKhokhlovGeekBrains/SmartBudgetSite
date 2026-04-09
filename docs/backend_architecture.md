## How to resume work

When continuing development in a new session:

1. Start by reviewing:
   - docs/backend_architecture.md
   - docs/feedback_workflow.md

2. Focus on:
   - "Sprint checkpoint" section (current state)
   - "Next sprint priorities" section

3. Then continue from the first unfinished item

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

Example:
- create function in `app/services/...`
- implement all validation and rules here

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

Completed:
- unified `get_db` usage via `app.dependencies`
- removed duplicate DB dependency definitions
- made `feedback_messages.email` nullable in model and database
- added Alembic migration for nullable email
- introduced service layer for feedback business logic
- moved email sending logic from `web/routes.py` to `app/services/feedback_service.py`
- moved publish/unpublish logic from `web/routes.py` to `app/services/feedback_service.py`
- added service tests for:
  - send feedback reply: missing email
  - send feedback reply: success
  - toggle publish: fail for non-product feedback
  - toggle publish: success
- admin UI now reflects email/publish status more clearly

Still not refactored:
- `admin_feedback_resolve`
- `admin_feedback_save_reply`

Next sprint priorities:
1. move resolve logic to service layer
2. move reply-draft save logic to service layer
3. add service tests for:
   - email already sent
   - missing admin reply
   - product_feedback is not allowed for email sending
   - cannot send email for published feedback
   - cannot publish without admin reply
   - toggle publish twice (publish -> unpublish)
4. review whether route tests are needed for critical admin actions after service coverage is complete