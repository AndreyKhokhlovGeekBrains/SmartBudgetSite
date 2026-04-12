from __future__ import annotations

from datetime import UTC, datetime

from app.models.feedback import FeedbackMessage
from app.repositories.feedback_admin_repository import FeedbackAdminRepository


def test_list_published_product_feedback_returns_only_published_product_feedback(db_session):
    repo = FeedbackAdminRepository(db_session)

    old_review = FeedbackMessage(
        type="product_feedback",
        name="User 1",
        email="u1@example.com",
        subject="Old review",
        message="Old message",
        admin_reply="Reply 1",
        is_published=True,
        published_at=datetime(2026, 4, 1, 10, 0, 0),
    )

    new_review = FeedbackMessage(
        type="product_feedback",
        name="User 2",
        email="u2@example.com",
        subject="New review",
        message="New message",
        admin_reply="Reply 2",
        is_published=True,
        published_at=datetime(2026, 4, 2, 10, 0, 0),
    )

    hidden_product_feedback = FeedbackMessage(
        type="product_feedback",
        name="User 3",
        email="u3@example.com",
        subject="Draft review",
        message="Draft message",
        admin_reply="Reply 3",
        is_published=False,
    )

    general_question = FeedbackMessage(
        type="general_question",
        name="User 4",
        email="u4@example.com",
        subject="Question",
        message="Question message",
        admin_reply="Reply 4",
        is_published=True,
        published_at=datetime(2026, 4, 3, 10, 0, 0),
    )

    db_session.add_all([
        old_review,
        new_review,
        hidden_product_feedback,
        general_question,
    ])
    db_session.commit()

    result = repo.list_published_product_feedback()

    assert len(result) == 2
    assert result[0].subject == "New review"
    assert result[1].subject == "Old review"


