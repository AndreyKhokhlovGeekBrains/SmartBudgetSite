from fastapi import APIRouter, Request, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.services.webhooks.calendly_webhook_service import (
    process_calendly_webhook,
)
from app.services.webhooks.signature_verification_service import (
    verify_webhook_signature,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/calendly")
async def calendly_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """
    Receive Calendly webhook events.

    Business rules:
    - This route must stay thin.
    - Signature verification, payload normalization, and lifecycle processing
      must be delegated to services.
    - The route must not update consultation entitlements directly.

    Side effects:
    - None yet. This is still webhook integration boundary scaffolding.

    Invariants / restrictions:
    - Do not parse Calendly-specific payload details in this route.
    - Do not create consultation entitlements from webhook requests.
    """

    raw_payload = await request.body()

    is_valid_signature = verify_webhook_signature(
        provider="calendly",
        payload=raw_payload,
        headers=request.headers,
    )

    if not is_valid_signature:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    payload = await request.json()

    process_calendly_webhook(
        db=db,
        payload=payload,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)