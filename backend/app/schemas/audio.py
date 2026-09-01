from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class AudioAnalysisResponse(BaseModel):
    recording_id: str
    quality: str
    category: str
    classification: str = Field(..., description="'Normal' or 'Abnormal'")
    prediction: str = Field(..., description="Specific diagnosis (e.g., 'Normal', 'Wheezing', 'Mid Systolic Murmur')")
    confidence: float
    waveform_data: List[float]
    spectrogram_image: str
    gradcam_image: str
    class_probabilities: Optional[Dict[str, float]] = None
    inference_time_ms: Optional[float] = None
    clinical_explanation: Optional[str] = None
    disease_progression: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
