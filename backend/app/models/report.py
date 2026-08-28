import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recording_id = Column(String(36), ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    report_title = Column(String(255), nullable=False)
    patient_identifier = Column(String(100), nullable=False)
    primary_diagnosis = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False, default="normal")  # 'normal', 'mild', 'moderate', 'severe'
    clinical_summary = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="draft")  # 'draft', 'finalized', 'archived'
    created_at = Column(DateTime(timezone=True), default=get_utc_now)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    user = relationship("User", back_populates="reports")
    recording = relationship("Recording", back_populates="reports")
    analysis = relationship("Analysis", back_populates="reports")
