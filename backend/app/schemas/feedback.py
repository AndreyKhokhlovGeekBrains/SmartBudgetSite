from pydantic import BaseModel, ConfigDict, EmailStr, Field


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