# Public Feedback Content Model

## Goal
Define how raw feedback messages can be transformed into public-facing content.

## Input source
Raw inbound messages are stored in `feedback_messages`.

These messages are private by default and should not be shown publicly as-is.

## Public content types

### 1. FAQ entry
Used when a user question is generally useful for other users.

Structure:
- question
- answer
- related product (optional)
- visibility flag
- sort order

### 2. Public product Q&A
Used when a product-related user question and founder reply are worth showing on the product page.

Structure:
- product reference
- user question
- founder reply
- publication status
- created_at
- optional display name / anonymized author label

### 3. Public review with reply
Used when a user sends positive/valuable product feedback and the founder wants to publish it.

Structure:
- product reference
- review text
- founder reply
- publication status
- created_at
- optional display name / anonymized author label

## Suggested admin workflow
1. User submits message through feedback form
2. Message appears in internal feedback inbox
3. Admin reviews message
4. Admin chooses one of the outcomes:
   - resolve privately
   - reply by email
   - convert to FAQ
   - convert to public Q&A
   - convert to public review

## Important rule
Raw inbox content and public content must remain separate entities.
Public content should always be curated and explicitly approved before display.