from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

# Determine if we are using SQLite to configure check_same_thread
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Declarative base
Base = declarative_base()

# FastAPI db dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
