# Feedback Operations MVP

## Goal
Create an internal technical page for reviewing and processing feedback messages submitted by users.

Important MVP direction:

This page is intended as a lightweight operational tool for a solo founder.

The goal is operational clarity and low-friction customer support handling, not a full support desk or CRM platform.

The workflow should remain:

* simple
* fast to maintain
* operationally sustainable for one person

Advanced support system features are intentionally postponed until after real product validation.

## Why
The feedback form already stores messages in the database, but there is no convenient internal interface to:
- review incoming messages
- inspect message type, email, subject, and text
- see attachments
- mark messages as resolved
- prioritize product feedback vs site issues

## MVP scope
- Internal page with list of feedback messages
- Sort by newest first
- Show:
  - created_at
  - type
  - email
  - subject
  - is_resolved
- Open one message in detail view
- Show attachment list with links
- Ability to mark message as resolved / unresolved

## Likely backend work
- GET endpoint for feedback list
- GET endpoint for feedback details
- POST/PATCH endpoint to update resolved status

## Likely frontend work
- New internal template page
- Table or card list for messages
- Detail block/page for one message
- Resolve button

## Later improvements
- Filters by message type
- Filters by resolved status
- Search by email / subject
- Pagination
- Auth protection
- S3-based attachment storage

## Explicit non-goals (MVP stage)

The feedback system intentionally does NOT aim to become:

* a helpdesk platform
* a ticketing system
* a threaded support inbox
* a CRM
* a live chat system
* a customer success platform

The MVP objective is:

* receive feedback
* respond once if needed
* publish useful reviews
* maintain operational visibility

Complex support workflows should only be considered after significant real customer volume appears.
