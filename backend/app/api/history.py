from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.recording import Recording
from app.models.analysis import Analysis
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/history", tags=["Screening History & Analytics"])


@router.get("/")
def get_user_screening_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by 'heart', 'lung', or 'mixed'"),
    classification: Optional[str] = Query(None, description="Filter by 'Normal' or 'Abnormal'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Returns a paginated list of the current user's past analyses.
    Strictly scoped to the authenticated user's ownership.
    """
    query = (
        db.query(Recording, Analysis)
        .outerjoin(Analysis, Recording.id == Analysis.recording_id)
        .filter(Recording.user_id == current_user.id)
    )

    if category:
        query = query.filter(Recording.sound_category == category.lower())

    # Get all recordings for the user matching category
    total = query.count()
    records = query.order_by(Recording.created_at.desc()).offset(skip).limit(limit).all()

    items = []
    for rec, ana in records:
        pred = ana.predicted_class if ana else None
        cls_val = "Normal" if pred and "normal" in pred.lower() else ("Abnormal" if pred else "Unanalyzed")
        
        if classification and cls_val.lower() != classification.lower():
            continue

        items.append({
            "recording_id": rec.id,
            "analysis_id": ana.id if ana else None,
            "date": rec.created_at,
            "category": rec.sound_category,
            "chest_location": rec.chest_location,
            "file_name": rec.file_name,
            "duration_seconds": rec.duration_seconds,
            "classification": cls_val,
            "prediction": pred or "Pending Analysis",
            "confidence": float(ana.confidence_score) if ana else None,
            "has_report": len(rec.reports) > 0,
            "patient_gender": rec.patient_gender,
            "patient_age": rec.patient_age,
        })

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get("/stats")
def get_screening_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Computes summary metrics strictly for the authenticated user's recordings."""
    recordings = db.query(Recording).filter(Recording.user_id == current_user.id).all()
    total_screenings = len(recordings)

    heart_count = sum(1 for r in recordings if r.sound_category == "heart")
    lung_count = sum(1 for r in recordings if r.sound_category == "lung")
    mixed_count = sum(1 for r in recordings if r.sound_category == "mixed")

    analyzed_recordings = [r for r in recordings if r.analysis is not None]
    normal_count = sum(1 for r in analyzed_recordings if "normal" in r.analysis.predicted_class.lower())
    abnormal_count = len(analyzed_recordings) - normal_count

    return {
        "total_screenings": total_screenings,
        "analyzed_count": len(analyzed_recordings),
        "normal_findings": normal_count,
        "abnormal_findings": abnormal_count,
        "category_distribution": {
            "heart": heart_count,
            "lung": lung_count,
            "mixed": mixed_count,
        },
    }
