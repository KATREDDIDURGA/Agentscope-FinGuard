from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
import os

# Ensure the database folder exists
os.makedirs("app/db", exist_ok=True)

# SQLite URL for local development
DATABASE_URL = "sqlite:///./app/db/fin_guard.db"

# Create the engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize tables (call once from main or init script)
def init_db():
    Base.metadata.create_all(bind=engine)