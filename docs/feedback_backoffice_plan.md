# Feedback Backoffice Plan

## Goal
Create an internal technical page for reviewing and processing feedback messages submitted by users.

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