from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class FeedbackCreate(BaseModel):
    message_type: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    subject: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=10)
    name: str | None = Field(default=None, max_length=200)
    page_url: str | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


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