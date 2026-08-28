import os
import uuid
import wave
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.recording import Recording
from app.models.analysis import Analysis
from app.schemas.recording import RecordingResponse
from app.schemas.audio import AudioAnalysisResponse
from app.core.dependencies import get_current_active_user
from app.services.ml_service import run_screening_inference

router = APIRouter(prefix="/audio", tags=["Audio Management & AI Screening"])


def get_wav_duration_and_params(filepath: str):
    """Extracts duration, sample rate, and channels from a WAV audio file."""
    try:
        with wave.open(filepath, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            channels = wf.getnchannels()
            duration = frames / float(rate)
            return duration, rate, channels
    except Exception:
        file_size = os.path.getsize(filepath)
        default_rate = 4000
        default_channels = 1
        duration = max(1.0, file_size / (default_rate * default_channels * 2))
        return duration, default_rate, default_channels


@router.post("/upload", response_model=RecordingResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio_recording(
    file: UploadFile = File(..., description="Audio file (.wav)"),
    sound_category: str = Form(..., description="'heart', 'lung', or 'mixed'"),
    chest_location: str = Form(..., description="e.g. Apex, LUSB, RUSB, LLSB, RC, LC"),
    patient_gender: Optional[str] = Form(None, description="M, F, or Other"),
    patient_age: Optional[int] = Form(None),
    clinical_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Uploads a WAV audio recording from digital stethoscope,
    validates format and duration, stores the file, and registers a recording record.
    """
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .wav audio files are supported for clinical sound screening.",
        )
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    duration, sample_rate, channels = get_wav_duration_and_params(file_path)
    
    if duration < 0.5:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio duration too short for clinical screening (minimum 0.5 seconds required).",
        )
    
    recording = Recording(
        id=file_id,
        user_id=current_user.id,
        sound_category=sound_category.lower(),
        chest_location=chest_location,
        file_path=file_path,
        file_name=file.filename,
        duration_seconds=round(duration, 2),
        sample_rate=sample_rate,
        channels=channels,
        patient_gender=patient_gender,
        patient_age=patient_age,
        clinical_notes=clinical_notes,
    )
    
    db.add(recording)
    db.commit()
    db.refresh(recording)
    
    return recording


@router.post("/analyze", response_model=AudioAnalysisResponse, status_code=status.HTTP_200_OK)
async def analyze_audio_recording(
    recording_id: Optional[str] = Form(None, description="ID of previously uploaded recording"),
    file: Optional[UploadFile] = File(None, description="Direct WAV file upload to analyze"),
    sound_category: Optional[str] = Form("heart", description="'heart', 'lung', or 'mixed'"),
    chest_location: Optional[str] = Form("Apex"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Executes full AI Screening Pipeline:
    1. Preprocessing (Librosa noise reduction, SciPy bandpass filtering, normalization)
    2. Mel-Spectrogram generation
    3. CNN Classification (Normal/Abnormal + Category + Confidence)
    4. Grad-CAM visual heatmap generation
    5. Saves result to `analyses` table
    6. Returns structured response with waveform, spectrogram, and Grad-CAM overlay.
    """
    if recording_id:
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
        audio_path = recording.file_path
        category = recording.sound_category
    elif file:
        if not file.filename.lower().endswith(".wav"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .wav audio files are supported for clinical screening.",
            )
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        rec_id = str(uuid.uuid4())
        stored_filename = f"{rec_id}_{file.filename}"
        audio_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
        
        content = await file.read()
        with open(audio_path, "wb") as f:
            f.write(content)
        
        duration, sample_rate, channels = get_wav_duration_and_params(audio_path)
        category = sound_category.lower() if sound_category else "heart"
        
        recording = Recording(
            id=rec_id,
            user_id=current_user.id,
            sound_category=category,
            chest_location=chest_location or "Apex",
            file_path=audio_path,
            file_name=file.filename,
            duration_seconds=round(duration, 2),
            sample_rate=sample_rate,
            channels=channels,
        )
        db.add(recording)
        db.commit()
        db.refresh(recording)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'recording_id' or 'file' must be provided for AI analysis.",
        )
    
    # Run full AI inference pipeline
    inference_result = run_screening_inference(
        audio_path=audio_path,
        category=category,
    )
    
    # Save or update in `analyses` table
    existing_analysis = db.query(Analysis).filter(Analysis.recording_id == recording.id).first()
    
    if existing_analysis:
        existing_analysis.predicted_class = inference_result["prediction"]
        existing_analysis.confidence_score = inference_result["confidence"]
        existing_analysis.class_probabilities = inference_result["class_probabilities"]
        existing_analysis.inference_time_ms = inference_result["inference_time_ms"]
        db.commit()
        db.refresh(existing_analysis)
    else:
        new_analysis = Analysis(
            id=str(uuid.uuid4()),
            recording_id=recording.id,
            predicted_class=inference_result["prediction"],
            confidence_score=inference_result["confidence"],
            class_probabilities=inference_result["class_probabilities"],
            mel_spectrogram_path=f"base64_spectrogram_{recording.id}",
            gradcam_heatmap_path=f"base64_gradcam_{recording.id}",
            anomaly_regions=[],
            inference_time_ms=inference_result["inference_time_ms"],
            model_version="v1.0.0",
        )
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
    
    return AudioAnalysisResponse(
        recording_id=recording.id,
        quality=inference_result["quality"],
        category=inference_result["category"],
        classification=inference_result["classification"],
        prediction=inference_result["prediction"],
        confidence=inference_result["confidence"],
        waveform_data=inference_result["waveform_data"],
        spectrogram_image=inference_result["spectrogram_image"],
        gradcam_image=inference_result["gradcam_image"],
        class_probabilities=inference_result["class_probabilities"],
        inference_time_ms=inference_result["inference_time_ms"],
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
def get_recording_by_id(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Fetches metadata for a specific audio recording."""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
    return recording


@router.get("/{recording_id}/file")
def get_audio_file(
    recording_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Streams the raw audio file for playback in the web player."""
    recording = db.query(Recording).filter(Recording.id == recording_id).first()
    if not recording or not os.path.exists(recording.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")
    
    return FileResponse(
        path=recording.file_path,
        media_type="audio/wav",
        filename=recording.file_name,
    )
