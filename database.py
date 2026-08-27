import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Fallback default now points to 'db' (the Docker service name) instead of 'localhost'
DEFAULT_DB_URL = "postgresql://postgres:Deblin@db:5432/aiia_ctms"

# 2. Read full DATABASE_URL from Docker environment if present
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()