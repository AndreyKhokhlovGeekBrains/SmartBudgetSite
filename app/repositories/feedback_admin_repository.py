from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.feedback import FeedbackMessage


class FeedbackAdminRepository:
    """
    Repository for internal feedback backoffice operations.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_feedback(self) -> list[FeedbackMessage]:
        """
        Return all feedback messages ordered by unresolved first, then newest first.
        """
        stmt = (
            select(FeedbackMessage)
            .order_by(
                FeedbackMessage.is_resolved.asc(),
                FeedbackMessage.created_at.desc(),
            )
        )
        return list(self.db.scalars(stmt).all())

    def get_feedback_by_id(self, feedback_id: int) -> FeedbackMessage | None:
        """
        Return one feedback message by id, or None if not found.
        """
        stmt = select(FeedbackMessage).where(FeedbackMessage.id == feedback_id)
        return self.db.scalar(stmt)

    def update_resolved_status(
        self,
        feedback_id: int,
        is_resolved: bool,
    ) -> FeedbackMessage | None:
        """
        Update resolved status for one feedback message.
        """
        feedback = self.get_feedback_by_id(feedback_id)
        if feedback is None:
            return None

        feedback.is_resolved = is_resolved
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def list_published_product_feedback(self, product_id: int):
        return (
            self.db.query(FeedbackMessage)
            .filter(
                FeedbackMessage.type == "product_feedback",
                FeedbackMessage.is_published.is_(True),
                FeedbackMessage.product_id == product_id,
            )
            .order_by(FeedbackMessage.published_at.desc())
            .all()
        )