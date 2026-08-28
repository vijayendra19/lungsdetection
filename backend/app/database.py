import os
import uuid
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("uvicorn")

Base = declarative_base()

# Attempt to connect to configured DATABASE_URL (PostgreSQL)
# Fallback to local SQLite if PostgreSQL server is not currently running.
db_url = settings.DATABASE_URL
engine = None

try:
    if db_url.startswith("postgresql"):
        temp_engine = create_engine(db_url, pool_pre_ping=True)
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = temp_engine
        print(f"Connected to primary database: {db_url.split('@')[-1]}")
except Exception as e:
    print(f"Notice: Primary PostgreSQL ({db_url}) not reachable. Falling back to local SQLite database.")
    db_url = "sqlite:///./smart_stethoscope.db"

if engine is None:
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes database tables and seeds demo clinician account if not present."""
    from app.models import User, Recording, Analysis, Report  # Import models
    from app.core.security import get_password_hash
    
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed default clinician user: dr.smith@hospital.org / SecurePassword123!
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "dr.smith@hospital.org").first()
        if not demo_user:
            demo_user = User(
                id=str(uuid.uuid4()),
                email="dr.smith@hospital.org",
                hashed_password=get_password_hash("SecurePassword123!"),
                full_name="Dr. Sarah Smith, MD",
                role="clinician",
                is_active=True,
            )
            db.add(demo_user)
            db.commit()
            print("Auto-seeded demo clinician: dr.smith@hospital.org / SecurePassword123!")
    except Exception as e:
        print(f"Notice: Could not seed demo user: {e}")
        db.rollback()
    finally:
        db.close()


# Run schema creation & demo seeding
init_db()


def get_db():
    """FastAPI dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
