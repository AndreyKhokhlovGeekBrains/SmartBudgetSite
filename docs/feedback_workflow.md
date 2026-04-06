# Feedback Workflow

## Purpose

This document describes how feedback messages are handled in the admin UI and what business rules apply to each message type.

---

## Feedback message types

### 1. `site_issue`
Purpose:
- private support only
- should not be published publicly

Expected handling:
- admin reviews the message
- admin prepares a reply draft
- admin may send one email reply to the user if an email is available
- after that, further communication should continue in the email client, not in admin UI

Publication rules:
- must never be published as a public review

---

### 2. `general_question`
Purpose:
- private communication only
- should not be published publicly

Expected handling:
- admin reviews the message
- admin prepares a reply draft
- admin may send one email reply to the user if an email is available
- after that, further communication should continue in the email client, not in admin UI

Publication rules:
- must never be published as a public review

---

### 3. `product_feedback`
Purpose:
- product-related feedback from the user
- may be handled privately and may optionally become a public review

Expected handling:
- admin reviews the message
- admin prepares a reply draft
- admin may send one email reply to the user if an email is available
- alternatively, admin may publish the feedback as a public review
- once published, email sending from admin UI is no longer allowed

Publication rules:
- only `product_feedback` can be published
- publication requires non-empty `admin_reply`
- when published:
  - `is_published = true`
  - `published_at` is set
- when unpublished:
  - `is_published = false`
  - `published_at = null`

---

## Admin UI workflow

### List page
The admin list page shows:
- feedback id
- created_at
- type
- email
- subject
- resolved status

Sorting:
- unresolved messages first
- newest messages first inside each group

---

### Detail page
The detail page allows admin to:
- view message details
- mark message as resolved / open
- edit reply draft
- send one email reply
- publish / unpublish product feedback as a public review

---

## Reply Draft

`admin_reply` is an internal draft stored in the database.

Important:
- it is not sent automatically
- it can be edited at any time before sending email
- it is also used as the required admin response before public review publication

---

## Email sending rules

Admin UI currently treats email sending as a one-time action.

Rules:
- email can be sent only if `admin_reply` is not empty
- email cannot be sent more than once from admin UI
- if `reply_sent_at` is set, repeated sending is blocked
- after first send, further conversation should continue in the external email client
- if a review is already published, email sending from admin UI is blocked

Tracking fields:
- `reply_sent_at`
- `reply_sent_to_email`

Open question:
- define final rule for messages where `email` is empty
- especially important for `site_issue` and `general_question`, because currently email may be absent there

---

## Publication rules

Public review publication is allowed only for `product_feedback`.

Rules:
- publish button is shown only for `product_feedback`
- publish action is blocked for all other message types
- publish action requires non-empty `admin_reply`
- published reviews should later be shown on a public `/reviews` page

---

## Current design decision

Admin UI is not a full email client.

Design decision:
- admin prepares and sends the first reply from admin UI
- after that, the conversation moves to the normal email client
- admin UI should not implement full reply-thread management

---

## Next implementation priorities

1. Add tests for:
   - resolve toggle
   - reply draft save
   - send email rules
   - publish rules
   - type-specific restrictions

2. Define final email requirement rules:
   - what to do when `email` is missing
   - whether email should become mandatory for all message types or only for some flows

3. Only after that, implement public `/reviews` page