from app.models.feedback import FeedbackMessage


def test_send_email_fails_when_email_missing(client, db_session):
    """
    Test case: sending email reply when user email is missing

    What we verify:
    - Endpoint /admin/feedback/{id}/send-email is reachable
    - If feedback has no email:
        -> request is rejected
        -> HTTP 400 is returned
        -> correct error message is provided
    """

    feedback = FeedbackMessage(
        type="general_question",
        name="Test User",
        email=None,
        subject="Test subject",
        message="Test message",
        page_url="/feedback",
        user_agent="test-agent",
        admin_reply="Test reply",
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

    # print(response.status_code)
    # print(response.text)

    # Check HTTP response status
    assert response.status_code in (302, 303)
    assert response.headers["location"] == (
        f"/admin/feedback/{feedback.id}"
        "?error=Cannot%20send%20email:%20user%20email%20is%20missing"
    )

def test_send_email_success(client, db_session):
    """
    Test case: successful email sending via admin endpoint

    What we verify:
    - Endpoint /admin/feedback/{id}/send-email works for valid input
    - Response is a redirect (303)
    - reply_sent_at is set
    """
    feedback = FeedbackMessage(
        type="general_question",
        name="Test User",
        email="test@example.com",
        subject="Test subject",
        message="Test message",
        page_url="/feedback",
        user_agent="test-agent",
        admin_reply="Test reply",
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

    # Check redirect
    assert response.status_code == 303

    db_session.refresh(feedback)

    # Email should be marked as sent
    assert feedback.reply_sent_at is not None
    assert feedback.reply_sent_to_email == "test@example.com"