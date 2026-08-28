import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sound_category = Column(String(50), nullable=False, index=True)  # 'heart', 'lung', 'mixed'
    chest_location = Column(String(100), nullable=False)  # 'Apex', 'LUSB', 'RUSB', 'LLSB', 'RC', 'LC'
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    duration_seconds = Column(Float, nullable=False)
    sample_rate = Column(Integer, nullable=False, default=4000)
    channels = Column(Integer, nullable=False, default=1)
    patient_gender = Column(String(10), nullable=True)  # 'M', 'F', 'Other'
    patient_age = Column(Integer, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=get_utc_now)
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    user = relationship("User", back_populates="recordings")
    analysis = relationship("Analysis", back_populates="recording", uselist=False, cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="recording", cascade="all, delete-orphan")
