"""
Feedback service layer

Responsibility:
- Contains ALL business logic for feedback handling
- Validates rules (email, type, publish restrictions, etc.)
- Works with repository
- Raises HTTPException for invalid operations

Important:
- Routes must NOT contain business logic
- Routes only call service functions and return responses
"""


from datetime import datetime, UTC

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.feedback_admin_repository import FeedbackAdminRepository


def send_feedback_reply(db: Session, feedback_id: int) -> None:
    """
    Send admin reply to user by email.

    Business rules:
    - Feedback must exist
    - Email reply is allowed only for private message types
    - Reply text must be present
    - User email must be present
    - Email cannot be sent more than once
    - Email cannot be sent for published feedback
    """

    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404, detail="Feedback not found")

    if item.type not in ("general_question", "site_issue"):
        raise HTTPException(
            status_code=400,
            detail="Email reply is not applicable for this feedback type",
        )

    if not item.admin_reply:
        raise HTTPException(
            status_code=400,
            detail="Cannot send email without reply text",
        )

    if not item.email:
        raise HTTPException(
            status_code=400,
            detail="Cannot send email: user email is missing",
        )

    if item.reply_sent_at:
        raise HTTPException(
            status_code=400,
            detail="Email already sent",
        )

    if item.is_published:
        raise HTTPException(
            status_code=400,
            detail="Cannot send email for published review",
        )

    # Simulate sending email (later we replace with real SMTP)
    item.reply_sent_at = datetime.now(UTC)
    item.reply_sent_to_email = item.email

    db.commit()

def toggle_feedback_publish(db: Session, feedback_id: int) -> None:
    """
    Toggle public review publication for product feedback.

    Business rules:
    - Feedback must exist
    - Only product_feedback can be published
    - Admin reply must be present before publication
    - When published:
        -> is_published = True
        -> published_at is set
    - When unpublished:
        -> is_published = False
        -> published_at = None
    """

    repo = FeedbackAdminRepository(db)
    item = repo.get_feedback_by_id(feedback_id)

    if not item:
        raise HTTPException(status_code=404, detail="Feedback not found")

    if item.type != "product_feedback":
        raise HTTPException(
            status_code=400,
            detail="Only product feedback can be published",
        )

    if not item.admin_reply:
        raise HTTPException(
            status_code=400,
            detail="Cannot publish without admin reply",
        )

    item.is_published = not item.is_published
    item.published_at = datetime.now(UTC) if item.is_published else None

    db.commit()