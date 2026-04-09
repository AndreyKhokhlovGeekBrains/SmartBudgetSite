import pytest

from app.services.feedback_service import send_feedback_reply, toggle_feedback_publish
from app.models.feedback import FeedbackMessage
from fastapi import HTTPException


def test_send_feedback_reply_fails_when_email_missing(db_session):
    """
    Service test: should fail if email is missing
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

    with pytest.raises(HTTPException) as exc:
        send_feedback_reply(db=db_session, feedback_id=feedback.id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Cannot send email: user email is missing"

def test_send_feedback_reply_success(db_session):
    """
    Service test: successful email sending
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

    # Act
    send_feedback_reply(db=db_session, feedback_id=feedback.id)

    # Reload from DB
    db_session.refresh(feedback)

    # Assert
    assert feedback.reply_sent_at is not None
    assert feedback.reply_sent_to_email == "test@example.com"

def test_toggle_publish_fails_for_non_product_feedback(db_session):
    """
    Should fail if feedback type is not product_feedback
    """

    feedback = FeedbackMessage(
        type="general_question",  # NOT product_feedback
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

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        toggle_feedback_publish(db=db_session, feedback_id=feedback.id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Only product feedback can be published"

def test_toggle_publish_success(db_session):
    """
    Should successfully publish product feedback
    """

    feedback = FeedbackMessage(
        type="product_feedback",
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

    # Act
    toggle_feedback_publish(db=db_session, feedback_id=feedback.id)

    db_session.refresh(feedback)

    # Assert
    assert feedback.is_published is True
    assert feedback.published_at is not None

def test_send_email_allowed_only_for_private_types(db_session):
    """
    Test case: email sending is restricted by feedback type

    What we verify:
    - Email is allowed only for:
        -> general_question
        -> site_issue
    - Email is NOT allowed for:
        -> product_feedback
    """

    from app.models.feedback import FeedbackMessage
    from app.services.feedback_service import send_feedback_reply
    from fastapi import HTTPException

    # Allowed type
    allowed = FeedbackMessage(
        type="general_question",
        name="Test",
        email="test@example.com",
        subject="Subject",
        message="Message",
        page_url="/feedback",
        user_agent="test-agent",
        admin_reply="Reply",
        is_resolved=False,
        is_published=False,
    )

    db_session.add(allowed)
    db_session.commit()
    db_session.refresh(allowed)

    # Should NOT raise
    send_feedback_reply(db=db_session, feedback_id=allowed.id)

    # Forbidden type
    forbidden = FeedbackMessage(
        type="product_feedback",
        name="Test",
        email="test@example.com",
        subject="Subject",
        message="Message",
        page_url="/feedback",
        user_agent="test-agent",
        admin_reply="Reply",
        is_resolved=False,
        is_published=False,
    )

    db_session.add(forbidden)
    db_session.commit()
    db_session.refresh(forbidden)

    # Should raise
    with pytest.raises(HTTPException) as exc:
        send_feedback_reply(db=db_session, feedback_id=forbidden.id)

    assert exc.value.status_code == 400
    assert "not applicable" in str(exc.value.detail)