from fastapi.testclient import TestClient


def test_reviews_page_returns_200(client: TestClient) -> None:
    response = client.get("/reviews")

    assert response.status_code == 200
    assert "Reviews" in response.text or "Отзывы" in response.text

from datetime import datetime

from app.models.feedback import FeedbackMessage


def test_reviews_page_shows_only_published_product_feedback(client, db_session):
    published_review = FeedbackMessage(
        type="product_feedback",
        name="User 1",
        email="u1@example.com",
        subject="Visible review",
        message="This should be visible",
        admin_reply="Reply",
        is_published=True,
        published_at=datetime(2026, 4, 1, 10, 0, 0),
    )

    hidden_review = FeedbackMessage(
        type="product_feedback",
        name="User 2",
        email="u2@example.com",
        subject="Hidden review",
        message="This should NOT be visible",
        admin_reply="Reply",
        is_published=False,
    )

    general_question = FeedbackMessage(
        type="general_question",
        name="User 3",
        email="u3@example.com",
        subject="Question",
        message="Also should NOT be visible",
        admin_reply="Reply",
        is_published=True,
        published_at=datetime(2026, 4, 2, 10, 0, 0),
    )

    db_session.add_all([published_review, hidden_review, general_question])
    db_session.commit()

    response = client.get("/reviews")

    assert response.status_code == 200
    assert "Visible review" in response.text
    assert "Hidden review" not in response.text
    assert "Question" not in response.text