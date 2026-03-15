from fastapi import APIRouter
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackCreateResponse, FeedbackListResponse

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

@router.get("/feedback/recent", response_model=FeedbackListResponse)
def get_recent_feedback(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    repo = FeedbackRepository(db)
    items = repo.get_recent(limit=limit)

    return {
        "items": items,
        "count": len(items),
    }

@router.patch("/feedback/{feedback_id}/resolve")
def resolve_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    repo = FeedbackRepository(db)
    feedback = repo.mark_resolved(feedback_id)

    if feedback is None:
        return {"status": "not_found"}

    return {
        "status": "ok",
        "id": feedback.id,
        "is_resolved": feedback.is_resolved,
    }
