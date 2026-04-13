from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi.testclient import TestClient

from app.models.feedback import FeedbackMessage


def test_admin_send_email_route_success_redirects_and_sets_reply_sent(
    client: TestClient,
    db_session: Any,
) -> None:
    """
    Critical route test:
    POST /admin/feedback/{id}/send-email

    Verifies:
    - route is wired correctly
    - redirect happens after success
    - reply_sent_at is set in DB
    """

    feedback = FeedbackMessage(
        type="general_question",
        email="user@example.com",
        subject="Need help",
        message="Please clarify how this works.",
        admin_reply="Thanks, here is the answer.",
        is_resolved=False,
        is_published=False,
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = client.post(
        f"/admin/feedback/{feedback.id}/send-email",
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"].startswith(f"/admin/feedback/{feedback.id}")

    db_session.refresh(feedback)

    assert feedback.reply_sent_at is not None
    assert feedback.reply_sent_to_email == "user@example.com"


def test_admin_send_email_route_blocks_second_send_and_does_not_change_reply_sent(
    client: TestClient,
    db_session: Any,
) -> None:
    """
    Critical route test:
    repeated email sending must be blocked.

    Verifies:
    - route is wired to service validation
    - redirect happens after failure
    - existing reply_sent_at is preserved
    """

    original_sent_at = datetime.now().replace(tzinfo=None)

    feedback = FeedbackMessage(
        type="general_question",
        email="user@example.com",
        subject="Need help",
        message="Please clarify how this works.",
        admin_reply="Thanks, here is the answer.",
        is_resolved=False,
        is_published=False,
        reply_sent_at=original_sent_at,
        reply_sent_to_email="user@example.com",
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = client.post(
        f"/admin/feedback/{feedback.id}/send-email",
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"] == f"/admin/feedback/{feedback.id}?error=Email%20already%20sent"

    db_session.refresh(feedback)

    assert feedback.reply_sent_at == original_sent_at.replace(tzinfo=None)
    assert feedback.reply_sent_to_email == "user@example.com"


def test_admin_toggle_publish_route_success(
    client: TestClient,
    db_session: Any,
) -> None:
    """
    Critical route test:
    POST /admin/feedback/{id}/toggle-publish

    Verifies:
    - route is wired correctly
    - redirect happens after success
    - publish flag is toggled
    """

    feedback = FeedbackMessage(
        type="product_feedback",
        email="user@example.com",
        subject="Great product",
        message="I really like it.",
        admin_reply="Thanks for your feedback!",
        is_resolved=False,
        is_published=False,
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = client.post(
        f"/admin/feedback/{feedback.id}/publish",
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"].startswith(f"/admin/feedback/{feedback.id}")

    db_session.refresh(feedback)

    assert feedback.is_published is True
    assert feedback.published_at is not None


def test_admin_toggle_publish_route_unpublish(
    client: TestClient,
    db_session: Any,
) -> None:
    """
    Critical route test:
    unpublish flow

    Verifies:
    - route is wired correctly
    - redirect happens after success
    - publish flag is toggled back
    """

    feedback = FeedbackMessage(
        type="product_feedback",
        email="user@example.com",
        subject="Great product",
        message="I really like it.",
        admin_reply="Thanks for your feedback!",
        is_resolved=False,
        is_published=True,
        published_at=datetime.now(),
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)

    response = client.post(
        f"/admin/feedback/{feedback.id}/publish",
        follow_redirects=False,
    )

    assert response.status_code in (302, 303)
    assert response.headers["location"].startswith(f"/admin/feedback/{feedback.id}")

    db_session.refresh(feedback)

    assert feedback.is_published is False
    assert feedback.published_at is None

