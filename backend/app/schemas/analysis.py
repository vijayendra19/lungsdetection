from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AnomalyRegion(BaseModel):
    start_sec: float
    end_sec: float
    intensity: float
    description: Optional[str] = None


class AnalysisCreate(BaseModel):
    recording_id: str
    predicted_class: str
    confidence_score: float
    class_probabilities: Dict[str, float]
    mel_spectrogram_path: str
    gradcam_heatmap_path: str
    anomaly_regions: Optional[List[Dict[str, Any]]] = []
    inference_time_ms: float
    model_version: str = "v1.0.0"


class AnalysisResponse(BaseModel):
    id: str
    recording_id: str
    predicted_class: str
    confidence_score: float
    class_probabilities: Dict[str, float]
    mel_spectrogram_path: str
    gradcam_heatmap_path: str
    anomaly_regions: Optional[List[Dict[str, Any]]] = []
    inference_time_ms: float
    model_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
