from fastapi import APIRouter
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackCreateResponse

router = APIRouter(prefix="/v1", tags=["v1"])

@router.get("/health")
def health() -> dict:
    return {"status": "ok"}

@router.get("/version")
def version() -> dict:
    return {"version": "v1"}

@router.post("/feedback", response_model=FeedbackCreateResponse)
def create_feedback(
    payload: FeedbackCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    repo = FeedbackRepository(db)

    user_agent = request.headers.get("user-agent")

    feedback = repo.create(
        message_type=payload.message_type,
        email=str(payload.email),
        subject=payload.subject,
        message=payload.message,
        name=payload.name,
        page_url=payload.page_url,
        user_agent=user_agent,
    )

    return {
        "status": "ok",
        "id": feedback.id,
    }
