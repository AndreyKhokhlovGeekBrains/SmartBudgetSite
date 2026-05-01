from datetime import datetime
from pydantic import BaseModel, EmailStr


class PurchaseItem(BaseModel):
    sale_id: int
    product_id: int
    product_name: str | None = None
    product_slug: str | None = None
    edition: str | None = None
    created_at: datetime | None = None
    item_type: str


class PurchaseLookupRequest(BaseModel):
    email: EmailStr


class PurchaseLookupResponse(BaseModel):
    verified: bool
    purchases: list[PurchaseItem]