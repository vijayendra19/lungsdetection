import os
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.recording import Recording
from app.models.analysis import Analysis
from app.core.dependencies import get_current_active_user
from app.services.audio_processing import preprocess_audio_pipeline
from app.services.ml_service import ModelLoader
from app.services.gradcam import compute_gradcam, generate_gradcam_overlay
from app.services.report_service import get_clinical_explanation
import numpy as np

router = APIRouter(prefix="/analysis", tags=["AI Audio Analysis Details"])


@router.get("/{analysis_id}")
def get_analysis_detail(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Returns full detail for one analysis including spectrogram, Grad-CAM,
    waveform data, probabilities, and plain-language explanation.
    Enforces strict user ownership check.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found")

    recording = analysis.recording
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated recording not found")

    # Ownership check
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view this analysis record.",
        )

    # Reconstruct/extract visual assets and waveform
    waveform_data = []
    spectrogram_image = None
    gradcam_image = None
    quality = "Good"

    if os.path.exists(recording.file_path):
        pipe = preprocess_audio_pipeline(recording.file_path, target_sr=4000)
        waveform_data = pipe["waveform_data"]
        spectrogram_image = pipe["spectrogram_image"]
        quality = pipe["quality"]

        # Compute Grad-CAM
        try:
            model = ModelLoader.get_instance().get_model(recording.sound_category.lower())
            tensor = pipe["spectrogram_array"][np.newaxis, :, :, np.newaxis]
            heatmap = compute_gradcam(model, tensor)
            gradcam_image = generate_gradcam_overlay(pipe["spectrogram_array"], heatmap)
        except Exception:
            gradcam_image = spectrogram_image

    classification = "Normal" if "normal" in analysis.predicted_class.lower() else "Abnormal"
    explanation = get_clinical_explanation(
        category=recording.sound_category,
        prediction=analysis.predicted_class,
        classification=classification,
        confidence=float(analysis.confidence_score),
    )

    return {
        "id": analysis.id,
        "recording_id": recording.id,
        "date": analysis.created_at,
        "file_name": recording.file_name,
        "category": recording.sound_category,
        "chest_location": recording.chest_location,
        "duration_seconds": recording.duration_seconds,
        "sample_rate": recording.sample_rate,
        "quality": quality,
        "classification": classification,
        "prediction": analysis.predicted_class,
        "confidence": float(analysis.confidence_score),
        "class_probabilities": analysis.class_probabilities,
        "waveform_data": waveform_data,
        "spectrogram_image": spectrogram_image,
        "gradcam_image": gradcam_image,
        "inference_time_ms": float(analysis.inference_time_ms),
        "clinical_explanation": explanation,
        "patient_gender": recording.patient_gender,
        "patient_age": recording.patient_age,
        "clinical_notes": recording.clinical_notes,
        "model_version": analysis.model_version,
    }


@router.get("/by-recording/{recording_id}")
def get_analysis_by_recording(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieves analysis record by recording ID with ownership check."""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view this recording.",
        )

    analysis = recording.analysis
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found for this recording")

    return get_analysis_detail(analysis.id, db, current_user)
