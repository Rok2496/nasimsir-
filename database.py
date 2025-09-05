from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Render uses a slightly different format for PostgreSQL URLs
# Convert postgres:// to postgresql:// if needed
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# For Render, we might need to handle SSL requirements
# Check if we're in a production environment
if os.getenv("RENDER"):
    # Render provides the database URL directly
    # Add SSL configuration for Render
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    # Local development
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()