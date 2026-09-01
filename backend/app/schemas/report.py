from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ReportCreate(BaseModel):
    recording_id: str
    analysis_id: str
    report_title: str = Field(..., max_length=255)
    patient_identifier: str = Field(..., max_length=100)
    primary_diagnosis: str = Field(..., max_length=255)
    severity: str = Field("normal", description="'normal', 'mild', 'moderate', 'severe'")
    clinical_summary: str
    recommendations: Optional[str] = None
    status: Optional[str] = Field("draft", description="'draft', 'finalized', 'archived'")


class ReportUpdate(BaseModel):
    report_title: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    severity: Optional[str] = None
    clinical_summary: Optional[str] = None
    recommendations: Optional[str] = None
    status: Optional[str] = None


class ReportResponse(BaseModel):
    id: str
    user_id: str
    recording_id: str
    analysis_id: str
    report_title: str
    patient_identifier: str
    primary_diagnosis: str
    severity: str
    clinical_summary: str
    recommendations: Optional[str] = None
    status: str
    chest_location: Optional[str] = None
    sound_category: Optional[str] = None
    confidence: Optional[float] = None
    clinical_explanation: Optional[str] = None
    disease_progression: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
