from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from datetime import datetime


class FeedbackCreate(BaseModel):
    message_type: str = Field(..., min_length=3, max_length=30)
    email: EmailStr | None = None
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10)
    name: str | None = Field(default=None, max_length=200)
    page_url: str | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    @model_validator(mode="after")
    def validate_email_for_product_feedback(self):
        if self.message_type == "product_feedback" and not self.email:
            raise ValueError("Email is required for product feedback.")
        return self


class FeedbackCreateResponse(BaseModel):
    status: str
    id: int

class FeedbackItemResponse(BaseModel):
    id: int
    type: str
    email: EmailStr
    subject: str
    message: str
    name: str | None = None
    page_url: str | None = None
    user_agent: str | None = None
    is_resolved: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class FeedbackListResponse(BaseModel):
    items: list[FeedbackItemResponse]
    count: int