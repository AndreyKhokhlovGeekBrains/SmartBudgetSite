# Feedback and Reviews Architecture

## 1. Internal feedback inbox
Purpose: collect and process incoming user messages.

This is a private/internal area for the product owner.

Includes:
- general questions
- site issues
- product feedback
- attachments
- sender email
- resolution status

Suggested route:
- /admin/feedback

Main actions:
- review message
- mark as resolved / unresolved
- open attachments
- manually reply to sender by email

## 2. Public reviews / testimonials
Purpose: show approved product feedback publicly on the site.

This is a public-facing feature and should be separated from raw feedback inbox.

Suggested placement:
- product landing page
- products page

Important rule:
Not every feedback message becomes a public review.
Only selected and approved product feedback should be shown publicly.

## 3. Suggested separation of concerns
- feedback_messages = raw inbound support / feedback inbox
- public_reviews = curated testimonials approved for display

## 4. Recommended implementation order
1. Build internal backoffice UI for feedback inbox
2. Add filters and detail view
3. Add manual workflow for selecting messages suitable for public reviews
4. Later introduce a separate public reviews model and UI block on landing pages