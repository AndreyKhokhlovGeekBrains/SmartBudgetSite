from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackCreateResponse
from app.repositories.feedback_repository import FeedbackRepository

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackCreateResponse)
def create_feedback_endpoint(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
):
    repo = FeedbackRepository(db)

    created = repo.create(
        message_type=feedback.message_type,
        email=str(feedback.email),
        subject=feedback.subject,
        message=feedback.message,
        name=feedback.name,
        page_url=feedback.page_url,
    )

    return {
        "status": "ok",
        "id": created.id,
    }