# Legacy tests: kept for backward compatibility during refactoring.
# May be removed after full migration to service + route tests.


from app.models.feedback import FeedbackMessage
from tests.conftest import auth_client


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

    response = auth_client(client).post(
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

