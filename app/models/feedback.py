from datetime import datetime, UTC

from sqlalchemy import Boolean, DateTime, Text, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index

from app.core.db import Base


class FeedbackMessage(Base):
    __tablename__ = "feedback_messages"
    __table_args__ = (
        Index("ix_feedback_created_at", "created_at"),
        Index("ix_feedback_resolved", "is_resolved"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    page_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    attachments = relationship(
        "FeedbackAttachment",
        back_populates="feedback",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )