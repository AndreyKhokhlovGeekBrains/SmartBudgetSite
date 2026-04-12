from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi.testclient import TestClient

from app.models.feedback import FeedbackMessage


def test_admin_send_email_route_success_redirects_and_sets_reply_sent(
    client: TestClient,
    db_session: Any,
    monkeypatch,
) -> None:
    """
    Critical route test:
    POST /admin/feedback/{id}/send-email

    Verifies:
    - route is wired correctly
    - redirect happens after success
    - reply_sent_at is set in DB
    - real SMTP is NOT used
    """

    sent_calls: list[dict[str, str]] = []

    def fake_send_email(*, to_email: str, subject: str, body: str) -> None:
        sent_calls.append(
            {
                "to_email": to_email,
                "subject": subject,
                "body": body,
            }
        )

    # Important:
    # Patch the symbol where it is USED during service execution.
    # If feedback_service imports the function directly, patch there.
    monkeypatch.setattr(
        "app.services.feedback_service.send_email",
        fake_send_email,
    )

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

    assert len(sent_calls) == 1
    assert sent_calls[0]["to_email"] == "user@example.com"
    assert sent_calls[0]["subject"] == "SmartBudget: reply to your message"
    assert "Thanks, here is the answer." in sent_calls[0]["body"]


def test_admin_send_email_route_blocks_second_send_and_does_not_call_mailer(
    client: TestClient,
    db_session: Any,
    monkeypatch,
) -> None:
    """
    Critical route test:
    repeated email sending must be blocked.

    Verifies:
    - route is wired to service validation
    - redirect happens after failure
    - mailer is NOT called
    - existing reply_sent_at is preserved
    """

    sent_calls: list[dict[str, str]] = []

    def fake_send_email(*, to_email: str, subject: str, body: str) -> None:
        sent_calls.append(
            {
                "to_email": to_email,
                "subject": subject,
                "body": body,
            }
        )

    monkeypatch.setattr(
        "app.services.feedback_service.send_email",
        fake_send_email,
    )

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
    assert sent_calls == []