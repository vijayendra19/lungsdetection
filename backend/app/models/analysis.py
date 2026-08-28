import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(String(36), ForeignKey("recordings.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    predicted_class = Column(String(100), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)
    class_probabilities = Column(JSON, nullable=False)  # {"Normal": 0.05, "Mid Systolic Murmur": 0.88}
    mel_spectrogram_path = Column(String(500), nullable=False)
    gradcam_heatmap_path = Column(String(500), nullable=False)
    anomaly_regions = Column(JSON, default=list)  # [{"start_sec": 1.2, "end_sec": 2.1, "intensity": 0.92}]
    inference_time_ms = Column(Float, nullable=False)
    model_version = Column(String(50), nullable=False, default="v1.0.0")
    created_at = Column(DateTime(timezone=True), default=get_utc_now)

    # Relationships
    recording = relationship("Recording", back_populates="analysis")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")
