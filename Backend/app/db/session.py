import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

def create_db_engine():
    target_url = settings.DATABASE_URL
    try:
        # Try connecting to PostgreSQL if configured
        if "postgresql" in target_url:
            engine = create_engine(target_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            # Test connection
            with engine.connect() as conn:
                logger.info("Successfully connected to PostgreSQL database.")
            return engine
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL at {target_url} ({e}). Falling back to local SQLite database.")
    
    # Fallback to local SQLite database
    sqlite_url = "sqlite:///./hydroponics.db"
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
