import io
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.recording import Recording
from app.models.analysis import Analysis
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse
from app.core.dependencies import get_current_active_user
from app.services.report_service import (
    generate_clinical_report_pdf,
    get_clinical_explanation,
)

router = APIRouter(tags=["Clinical Reports & PDF Generation"])


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_clinical_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generates and persists a structured clinical screening report."""
    recording = db.query(Recording).filter(Recording.id == report_in.recording_id).first()
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")

    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this recording.",
        )

    analysis = db.query(Analysis).filter(Analysis.id == report_in.analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")

    # If clinical_summary is empty or basic, generate comprehensive clinical explanation
    clinical_summary = report_in.clinical_summary
    if not clinical_summary or len(clinical_summary.strip()) < 10:
        clinical_summary = get_clinical_explanation(
            category=recording.sound_category,
            prediction=analysis.predicted_class,
            classification="Normal" if "normal" in analysis.predicted_class.lower() else "Abnormal",
            confidence=float(analysis.confidence_score),
        )

    report = Report(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        recording_id=recording.id,
        analysis_id=analysis.id,
        report_title=report_in.report_title or f"Screening Report - {recording.file_name}",
        patient_identifier=report_in.patient_identifier or "Anonymous Patient",
        primary_diagnosis=report_in.primary_diagnosis or analysis.predicted_class,
        severity=report_in.severity or "normal",
        clinical_summary=clinical_summary,
        recommendations=report_in.recommendations,
        status=report_in.status or "finalized",
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get("/{report_id}")
def get_report_or_pdf(
    report_id: str,
    format: Optional[str] = Query("json", description="'json' or 'pdf'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieves report summary with plain-language explanation and visual assets,
    or generates and streams the printable medical PDF report (when ?format=pdf).
    Accepts report_id, analysis_id, or recording_id. Enforces user ownership.
    """
    # 1. Search directly by Report.id
    report = db.query(Report).filter(Report.id == report_id).first()

    # 2. Search by Analysis ID or Recording ID if not found directly
    if not report:
        report = (
            db.query(Report)
            .filter((Report.analysis_id == report_id) | (Report.recording_id == report_id))
            .first()
        )

    # 3. If still no Report exists, check if an Analysis exists and auto-generate the report
    if not report:
        analysis = db.query(Analysis).filter(Analysis.id == report_id).first()
        recording = None
        if analysis:
            recording = analysis.recording
        else:
            recording = db.query(Recording).filter(Recording.id == report_id).first()
            if recording:
                analysis = (
                    db.query(Analysis)
                    .filter(Analysis.recording_id == recording.id)
                    .order_by(Analysis.created_at.desc())
                    .first()
                )

        if analysis and recording:
            # Ownership verification
            if recording.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You do not have permission to view this report.",
                )

            is_normal = "normal" in analysis.predicted_class.lower()
            explanation = get_clinical_explanation(
                category=recording.sound_category,
                prediction=analysis.predicted_class,
                classification="Normal" if is_normal else "Abnormal",
                confidence=float(analysis.confidence_score),
            )

            report = Report(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                recording_id=recording.id,
                analysis_id=analysis.id,
                report_title=f"Clinical Auscultation Report - {recording.file_name}",
                patient_identifier=f"PAT-{recording.id[:6].upper()}",
                primary_diagnosis=analysis.predicted_class,
                severity="normal" if is_normal else "moderate",
                clinical_summary=explanation,
                recommendations=(
                    "Routine annual cardiopulmonary follow-up."
                    if is_normal
                    else "Recommend 2D-Echocardiogram and formal cardiology consultation."
                ),
                status="finalized",
            )
            db.add(report)
            db.commit()
            db.refresh(report)

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinical report not found")

    # Ownership check
    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view this report.",
        )

    recording = report.recording
    analysis = report.analysis

    if format.lower() == "pdf":
        pdf_bytes = generate_clinical_report_pdf(
            report=report,
            recording=recording,
            analysis=analysis,
            clinician_name=current_user.full_name,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="clinical_report_{report.patient_identifier}.pdf"'
            },
        )

    explanation = get_clinical_explanation(
        category=recording.sound_category,
        prediction=analysis.predicted_class,
        classification="Normal" if "normal" in analysis.predicted_class.lower() else "Abnormal",
        confidence=float(analysis.confidence_score),
    )

    return {
        "id": report.id,
        "user_id": report.user_id,
        "recording_id": report.recording_id,
        "analysis_id": report.analysis_id,
        "report_title": report.report_title,
        "patient_identifier": report.patient_identifier,
        "primary_diagnosis": report.primary_diagnosis,
        "severity": report.severity,
        "clinical_summary": report.clinical_summary,
        "clinical_explanation": explanation,
        "recommendations": report.recommendations,
        "status": report.status,
        "sound_category": recording.sound_category,
        "chest_location": recording.chest_location,
        "confidence": float(analysis.confidence_score),
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


@router.get("/{report_id}/pdf")
def get_report_pdf_direct(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Direct route to download/stream the clinical PDF report."""
    return get_report_or_pdf(report_id, format="pdf", db=db, current_user=current_user)


@router.get("/", response_model=List[ReportResponse])
def list_user_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Lists all clinical reports created by the authenticated user."""
    return (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: str,
    report_in: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates an existing clinical report with ownership check."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not own this report.",
        )

    update_data = report_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report
