"""
Application dependencies.

Important:
- Use get_db from this module everywhere in routes
- Do not duplicate get_db in other modules
"""


from collections.abc import Generator
from sqlalchemy.orm import Session

from app.core.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    # Provide a database session per request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()