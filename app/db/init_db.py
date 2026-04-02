from app.core.db import Base, engine


def init_db() -> None:
    # create tables based on ORM models
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()