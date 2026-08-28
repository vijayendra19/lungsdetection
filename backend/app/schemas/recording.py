from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RecordingBase(BaseModel):
    sound_category: str = Field(..., description="'heart', 'lung', or 'mixed'")
    chest_location: str = Field(..., description="e.g. 'Apex', 'LUSB', 'RUSB', 'LLSB', 'RC', 'LC'")
    patient_gender: Optional[str] = Field(None, description="'M', 'F', or 'Other'")
    patient_age: Optional[int] = Field(None, ge=0, le=130)
    clinical_notes: Optional[str] = None


class RecordingCreate(RecordingBase):
    pass


class RecordingResponse(RecordingBase):
    id: str
    user_id: str
    file_path: str
    file_name: str
    duration_seconds: float
    sample_rate: int
    channels: int
    recorded_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
