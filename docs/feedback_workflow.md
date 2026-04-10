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

Admin UI treats email sending as a one-time action.

Rules:
- email can be sent for all feedback types (if email is available)

- email requires:
  - non-empty `admin_reply`
  - non-empty `email`

- email cannot be sent more than once:
  - if `reply_sent_at` is set, repeated sending is blocked

- email sending is blocked if:
  - feedback is already published (`is_published = true`)

After sending:
- `reply_sent_at` is set
- `reply_sent_to_email` is stored
- further communication must continue in external email client

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

1. review whether route tests are still needed for critical admin actions

2. isolate email sending in tests:
   - mock mail service in service/route tests
   - ensure tests never send real SMTP emails

3. only after that, implement public `/reviews` page

---

## Product Q&A (product_qna)

Purpose:
- store curated public questions and answers about products
- act as a knowledge base / FAQ

Important:
- Q&A entries are short and focused
- they are not full articles or guides

Source of data:
- Q&A is derived from feedback messages, but manually curated

Workflow:
1. user sends a message via feedback form
2. admin reviews the message
3. if it contains a useful question:
   - admin rewrites it into a clear question
   - writes a concise answer
4. Q&A can be published on product page

Difference from long-form content:
- Q&A = short answers
- articles/guides = separate feature (not implemented yet)

---

## Test coverage status

Covered by tests:
- send email:
  - missing email
  - success
  - type restriction
  - email already sent
  - missing admin reply
  - sending email for published feedback
- publish:
  - fail for non-product feedback
  - success
  - publish without admin reply
  - publish → unpublish toggle flow
- resolve:
  - toggle to resolved
  - toggle back to unresolved
- reply draft:
  - save success
  - empty reply normalization (`"" -> None`)

Note:
- tests currently need email sending isolation
- real SMTP sending must be mocked in automated tests

## Design clarification: feedback vs review vs Q&A

Although `product_feedback` messages can be used to create public content,
these concepts are intentionally separated:

- Feedback message:
  - raw user input
  - stored in `feedback_messages`
  - may remain private

- Public review:
  - derived from `product_feedback`
  - may reuse user message + admin reply
  - intended for `/reviews` page

- Product Q&A:
  - curated and rewritten content
  - not a direct copy of feedback
  - stored separately in `product_qna`

Important:
- feedback_messages should never be treated as final public content
- publication is a transformation, not a flag

## Future data model note

Current implementation uses `is_published` and `published_at` inside `feedback_messages`.

This is acceptable as a temporary admin workflow solution, but it should be treated as transitional.

Why:
- one feedback message may later need to produce:
  - a public review
  - a Q&A entry
  - or remain private only
- storing publication state inside `feedback_messages` couples raw input with public content lifecycle

Long-term direction:
- `feedback_messages` should remain the source of raw private input
- public reviews should eventually have their own table / entity
- `product_qna` should remain a separate curated entity