from sqlalchemy import create_engine, text
from app.core.config import settings

print("DATABASE_URL =", settings.DATABASE_URL)

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    row = conn.execute(
        text("SELECT current_database(), current_user, inet_server_addr(), inet_server_port(), current_schema()")
    ).fetchone()
    print("DB info =", row)

    rows = conn.execute(
        text("SELECT schemaname, tablename FROM pg_catalog.pg_tables WHERE schemaname='public' ORDER BY tablename")
    ).fetchall()
    print("Tables =", rows)