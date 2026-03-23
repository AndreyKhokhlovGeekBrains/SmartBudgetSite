from fastapi import APIRouter
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackCreate, FeedbackCreateResponse, FeedbackListResponse
from app.repositories.sales_repository import get_verified_purchases_by_email
from app.schemas.purchase_check import PurchaseLookupRequest, PurchaseLookupResponse, PurchaseItem

from fastapi import HTTPException
from app.repositories.sales_repository import is_verified_sale_for_email

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

    # 🔐 BACKEND VALIDATION
    if payload.message_type == "product_feedback":
        if not payload.email:
            raise HTTPException(
                status_code=400,
                detail="Email is required for product feedback",
            )

        if payload.sale_id is None:
            raise HTTPException(
                status_code=400,
                detail="Sale selection is required for product feedback",
            )

        if not is_verified_sale_for_email(
            db=db,
            sale_id=payload.sale_id,
            email=str(payload.email),
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid sale selection",
            )

    feedback = repo.create(
        message_type=payload.message_type,
        email=str(payload.email),
        subject=payload.subject,
        message=payload.message,
        name=payload.name,
        page_url=payload.page_url,
        user_agent=user_agent,
        # ⚠️ если модель поддерживает — добавь:
        # sale_id=payload.sale_id,
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

@router.post("/check-purchase", response_model=PurchaseLookupResponse)
def check_purchase(
    payload: PurchaseLookupRequest,
    db: Session = Depends(get_db),
) -> PurchaseLookupResponse:
    purchases_data = get_verified_purchases_by_email(
        db=db,
        email=str(payload.email),
    )

    purchases = [PurchaseItem(**item) for item in purchases_data]

    return PurchaseLookupResponse(
        verified=len(purchases) > 0,
        purchases=purchases,
    )
