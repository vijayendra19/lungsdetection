import io
import os
import base64
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import numpy as np

from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)


def get_disease_progression_details(category: str, prediction: str, classification: str) -> Dict[str, Any]:
    """Provides structured clinical differential diagnoses, progression risks, and diagnostic workup."""
    pred_lower = prediction.lower()
    cat_lower = category.lower()
    is_normal = "normal" in pred_lower or classification.lower() == "normal"
    
    if is_normal:
        return {
            "has_abnormality": False,
            "primary_condition": "Normal Physiological State",
            "potential_diseases": [],
            "progression_risks": "Normal acoustic profile with regular cardiac cadence (S1/S2) and vesicular breath sounds. No evidence of pathological structural remodeling or airway obstruction.",
            "recommended_workup": ["Routine annual health wellness checkup", "Standard preventive cardiovascular and pulmonary monitoring"],
            "urgency": "Low (Routine Baseline)",
        }
        
    # Abnormal Conditions
    if "mid systolic" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Aortic Valve Stenosis / Outflow Tract Obstruction",
            "potential_diseases": [
                "Aortic Valve Stenosis (Calcific / Bicuspid)",
                "Hypertrophic Cardiomyopathy (HOCM)",
                "Pulmonic Valve Stenosis",
                "Aortic Sclerosis",
            ],
            "progression_risks": "Untreated aortic stenosis forces the left ventricle to pump against high afterload resistance, leading to concentric Left Ventricular Hypertrophy (LVH), exertional angina, syncope, and eventual Congestive Heart Failure (HFrEF).",
            "recommended_workup": [
                "2D Transthoracic Echocardiogram (TTE) with Doppler gradient assessment",
                "12-Lead Electrocardiogram (ECG) to assess voltage criteria for LVH and strain",
                "Serum NT-proBNP / Troponin biomarker quantification",
                "Cardiology referral for surgical or Transcatheter Aortic Valve Replacement (TAVR) evaluation",
            ],
            "urgency": "High Priority (Cardiology Referral Recommended)",
        }
    elif "late systolic" in pred_lower or "holosystolic" in pred_lower or "mitral" in pred_lower or "regurgitation" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Mitral / Tricuspid Valve Regurgitation",
            "potential_diseases": [
                "Mitral Valve Prolapse (MVP / Barlow's Syndrome)",
                "Chronic Mitral Regurgitation",
                "Tricuspid Valve Incompetence",
                "Ventricular Septal Defect (VSD)",
            ],
            "progression_risks": "Chronic retrograde volume overload leads to Left Atrial Enlargement (LAE), secondary pulmonary venous hypertension, elevated stroke risk from Atrial Fibrillation, and progressive eccentric left ventricular dilation.",
            "recommended_workup": [
                "2D Echocardiogram with Color Flow Doppler mapping (regurgitant volume/fraction)",
                "24-Hour to 48-Hour Holter Monitor for supraventricular arrhythmias",
                "Chest Radiograph (PA view) for cardiomegaly and pulmonary venous congestion",
                "Evaluation for transcatheter edge-to-edge repair (MitraClip) or valve surgery",
            ],
            "urgency": "Moderate to High Priority",
        }
    elif "diastolic" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Aortic Regurgitation / Mitral Stenosis",
            "potential_diseases": [
                "Aortic Valve Regurgitation (Aortic Incompetence)",
                "Rheumatic Mitral Stenosis",
                "Tricuspid Stenosis",
            ],
            "progression_risks": "Diastolic murmurs are almost universally pathological. Persistent diastolic regurgitation causes severe left ventricular volume overload, elevated end-diastolic pressures, and rapid progression to acute pulmonary edema.",
            "recommended_workup": [
                "Urgent Comprehensive Transthoracic Echocardiogram (TTE)",
                "Cardiac Magnetic Resonance (CMR) Imaging for precise regurgitant fraction quantification",
                "Ambulatory Blood Pressure hemodynamic evaluation",
                "Prompt Formal Cardiology / Cardiothoracic Consultation",
            ],
            "urgency": "Urgent (Comprehensive Cardiac Workup Required)",
        }
    elif "s3" in pred_lower or "s4" in pred_lower or "gallop" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Elevated Filling Pressures & Ventricular Stiffness",
            "potential_diseases": [
                "Congestive Heart Failure (HFrEF / HFpEF)",
                "Hypertensive Cardiomyopathy",
                "Dilated Cardiomyopathy",
                "Ischemic Heart Disease / Coronary Artery Disease",
            ],
            "progression_risks": "Gallop sounds indicate stiffened ventricular walls and high filling pressures. If unmanaged, this progresses to decompensated heart failure exacerbations and frequent hospitalizations.",
            "recommended_workup": [
                "Serum NT-proBNP & Troponin I blood biomarkers",
                "2D Echocardiogram for Left Ventricular Ejection Fraction (LVEF) & diastolic function grading",
                "Chest X-Ray for Kerley B lines and pulmonary vascular cephalization",
                "Initiation/optimization of Guideline-Directed Medical Therapy (GDMT)",
            ],
            "urgency": "High Priority (Heart Failure Evaluation)",
        }
    elif "wheez" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Lower Airway Bronchospasm & Airway Obstruction",
            "potential_diseases": [
                "Bronchial Asthma (Acute Exacerbation)",
                "Chronic Obstructive Pulmonary Disease (COPD / Chronic Bronchitis / Emphysema)",
                "Acute Reactive Airway Bronchitis",
                "Cardiac Asthma (secondary to pulmonary venous congestion)",
            ],
            "progression_risks": "Ongoing airway narrowing causes air trapping, alveolar hyperinflation, ventilation-perfusion mismatch, respiratory muscle fatigue, and acute hypoxemic respiratory failure.",
            "recommended_workup": [
                "Spirometry / Pulmonary Function Tests (PFTs) with pre/post-bronchodilator reversibility",
                "Continuous Pulse Oximetry (SpO2) and Arterial Blood Gas (ABG) analysis",
                "Chest Radiograph (PA & Lateral views) to exclude pneumothorax or infiltration",
                "Inhaled Corticosteroid (ICS) + Long-Acting Beta Agonist (LABA) therapy assessment",
            ],
            "urgency": "Moderate to Urgent (if accompanying resting dyspnea)",
        }
    elif "crackle" in pred_lower or "crepitation" in pred_lower or "fine crackle" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Alveolar Infiltration & Interstitial Lung Pathology",
            "potential_diseases": [
                "Idiopathic Pulmonary Fibrosis (IPF) / Interstitial Lung Disease (ILD)",
                "Congestive Heart Failure with Alveolar Pulmonary Edema",
                "Bacterial or Viral Pneumonia / Pneumonitis",
                "Bronchiectasis / Atelectasis",
            ],
            "progression_risks": "Signifies fluid or fibrotic stiffness in terminal respiratory units. Left unaddressed, progressive parenchymal remodeling causes permanent gas-diffusion impairment, pulmonary arterial hypertension, and chronic hypoxia.",
            "recommended_workup": [
                "High-Resolution Computed Tomography (HRCT) of the Chest",
                "Diffusion Capacity of Carbon Monoxide (DLCO) & 6-Minute Walk Test",
                "2D Echocardiogram to differentiate cardiogenic vs non-cardiogenic pulmonary congestion",
                "Comprehensive Pulmonology referral",
            ],
            "urgency": "High Priority (Pulmonary Evaluation Required)",
        }
    elif "rhonchi" in pred_lower or "rub" in pred_lower or "stridor" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Large Airway Secretion Accumulation & Pleural Inflammation",
            "potential_diseases": [
                "Acute / Chronic Bronchitis",
                "Lobar / Broncho-Pneumonia",
                "Bronchiectasis with Secretion Stasis",
                "Pleurisy / Pleural Friction Rub",
            ],
            "progression_risks": "Mucus stasis increases the risk of severe bacterial superinfections, mucus plugging, lobar atelectasis, and progression to systemic sepsis.",
            "recommended_workup": [
                "Chest Radiography / High-Resolution Chest CT",
                "Sputum Culture, Gram Stain, and Cytology",
                "Complete Blood Count (CBC) with Differential and C-Reactive Protein (CRP)",
                "Targeted antimicrobial therapy and airway clearance physiotherapy",
            ],
            "urgency": "Moderate to High",
        }
    elif "mixed" in cat_lower or "mixed" in pred_lower:
        return {
            "has_abnormality": True,
            "primary_condition": "Combined Cardiopulmonary Syndrome",
            "potential_diseases": [
                "Cor Pulmonale (Right Heart Failure secondary to Severe COPD/ILD)",
                "Congestive Heart Failure with Secondary Pulmonary Edema & Reactive Airways",
                "Combined Valvular Heart Disease with Chronic Respiratory Disease",
            ],
            "progression_risks": "Dual cardiac and pulmonary disease accelerates biventricular hemodynamic failure, worsening hypoxemia and increasing hospital admission rates.",
            "recommended_workup": [
                "Simultaneous 2D Echocardiography + Full Pulmonary Function Testing (PFTs)",
                "Contrast CT Angiography / HRCT Chest",
                "Serum NT-proBNP and Arterial Blood Gas (ABG) panel",
                "Joint Multidisciplinary Cardio-Pulmonary Clinical Consultation",
            ],
            "urgency": "Urgent Priority (Multidisciplinary Workup Needed)",
        }
    else:
        return {
            "has_abnormality": True,
            "primary_condition": f"Auscultation Anomaly ({prediction})",
            "potential_diseases": [
                "Cardiovascular Structural / Valvular Abnormality",
                "Adventitious Respiratory Airway Pathology",
            ],
            "progression_risks": "Acoustic turbulence indicates mechanical or flow disruption within the cardiopulmonary tract requiring further diagnostic confirmation.",
            "recommended_workup": [
                "Follow-up Clinical Auscultation with High-Fidelity Digital Recording",
                "Confirmatory 2D Echocardiogram or Chest Radiograph",
                "Primary Physician / Specialist Evaluation",
            ],
            "urgency": "Moderate Priority",
        }


def get_clinical_explanation(category: str, prediction: str, classification: str, confidence: float) -> str:
    """Generates an evidence-based, plain-language clinical explanation of the AI auscultation findings."""
    pred_lower = prediction.lower()
    cat_lower = category.lower()
    
    if "normal" in pred_lower:
        if "heart" in cat_lower:
            return (
                "The acoustic auscultation demonstrates a regular physiological cardiac rhythm with crisp, "
                "well-defined S1 and S2 heart sounds. No pathological murmurs, clicks, or extra gallop sounds (S3/S4) "
                "were detected in the acoustic spectrogram. Frequency distribution remains within normal baseline limits."
            )
        elif "lung" in cat_lower:
            return (
                "The pulmonary auscultation demonstrates normal vesicular breath sounds with clear, laminar airflow "
                "throughout inspiration and expiration. No adventitious sounds such as crackles, wheezes, rhonchi, or pleural "
                "friction rubs are observed."
            )
        else:
            return (
                "Cardiopulmonary auscultation shows standard physiological acoustic parameters with synchronized cardiac cycle "
                "and clear respiratory phases without abnormal acoustic turbulence."
            )

    # Abnormal Heart Sounds
    if "heart" in cat_lower or "murmur" in pred_lower or "systolic" in pred_lower or "diastolic" in pred_lower:
        if "mid systolic" in pred_lower:
            return (
                "Acoustic analysis reveals diamond-shaped (crescendo-decrescendo) acoustic turbulence occurring between S1 and S2. "
                "Grad-CAM highlights localized energy concentration in the mid-frequency band (150–500 Hz), characteristic of mid-systolic ejection murmurs "
                "(e.g., aortic stenosis or pulmonary valve stenosis)."
            )
        elif "late systolic" in pred_lower:
            return (
                "Analysis indicates high-frequency acoustic energy commencing in mid-systole and persisting until the second heart sound (S2). "
                "The saliency heatmap emphasizes prolonged systolic turbulence commonly associated with mitral valve prolapse or mitral regurgitation."
            )
        elif "early systolic" in pred_lower:
            return (
                "Early systolic acoustic vibrations detected immediately following S1 and tapering before mid-systole. "
                "Commonly associated with acute mitral regurgitation or small ventricular septal defects."
            )
        elif "diastolic" in pred_lower:
            return (
                "Low-to-medium frequency acoustic rumbling detected during ventricular diastole. Diastolic murmurs are generally pathological "
                "and warrant echocardiographic evaluation for mitral stenosis or aortic regurgitation."
            )
        elif "atrial fibrillation" in pred_lower or "af" in pred_lower:
            return (
                "Acoustic rhythm analysis indicates variable R-R interval spacing with fluctuating S1 amplitude and absent physiological atrial gallop cadence, "
                "strongly indicative of atrial fibrillation."
            )
        elif "s3" in pred_lower:
            return (
                "A prominent low-frequency early diastolic sound (S3 gallop) is detected shortly after S2 during rapid passive ventricular filling, "
                "suggestive of elevated ventricular filling pressures or volume overload."
            )
        elif "s4" in pred_lower:
            return (
                "A low-frequency late diastolic sound (S4 gallop) is identified immediately preceding S1, indicating forceful atrial contraction against a non-compliant ventricle."
            )
        else:
            return (
                f"Abnormal cardiac acoustic patterns ({prediction}) identified with {confidence*100:.1f}% confidence. "
                "Significant acoustic energy is concentrated in anomalous frequency bands shown in the Grad-CAM heatmap."
            )

    # Abnormal Lung Sounds
    if "lung" in cat_lower or "wheez" in pred_lower or "crackle" in pred_lower or "rhonchi" in pred_lower or "rub" in pred_lower:
        if "wheez" in pred_lower:
            return (
                "Continuous, high-pitched musical acoustic oscillations (>400 Hz) detected predominantly during expiration. "
                "Grad-CAM demonstrates sustained horizontal harmonic energy bands reflecting turbulent airflow through narrowed airways (bronchospasm)."
            )
        elif "fine crackle" in pred_lower or "crackle" in pred_lower:
            return (
                "Discontinuous, explosive, high-pitched acoustic bursts identified during late inspiration. "
                "The Grad-CAM heatmap identifies localized temporal spikes typical of explosive reopening of collapsed peripheral airways."
            )
        elif "coarse crackle" in pred_lower:
            return (
                "Low-pitched, bubbling discontinuous acoustic transients occurring early in inspiration and expiration, "
                "indicative of fluid or mucus moving through larger airways."
            )
        elif "rhonchi" in pred_lower:
            return (
                "Continuous, low-pitched snoring/rattling acoustic signals (<200 Hz) with irregular harmonic structures, "
                "suggestive of airway secretions in central tracheobronchial passages."
            )
        elif "rub" in pred_lower:
            return (
                "Low-frequency grating or creaking acoustic transients during both inspiration and expiration, "
                "characteristic of friction between inflamed pleural surfaces."
            )

    return (
        f"AI screening identified {prediction} ({classification}) with {confidence*100:.1f}% confidence. "
        "Grad-CAM visual saliency emphasizes the focal acoustic regions that contributed most strongly to this classification."
    )


def generate_clinical_report_pdf(
    report: Any,
    recording: Any,
    analysis: Any,
    clinician_name: str = "Dr. Clinician",
) -> bytes:
    """
    Generates a PDF Clinical Screening Report using ReportLab.
    Embeds the Mel-Spectrogram and Grad-CAM saliency heatmaps.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Custom typography & styles
    primary_color = colors.HexColor("#1e293b")  # Slate 800
    accent_color = colors.HexColor("#2563eb")   # Blue 600
    risk_color = colors.HexColor("#dc2626") if "abnormal" in analysis.predicted_class.lower() or "abnormal" in str(report.primary_diagnosis).lower() else colors.HexColor("#16a34a")

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=10,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )
    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.white,
        alignment=1,  # Centered
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>SMART STETHOSCOPE AI</b><br/><font size=9 color='#64748b'>Cardiopulmonary Digital Auscultation & AI Screening Report</font>", title_style),
            Paragraph(f"<b>Report ID:</b> {str(report.id)[:8]}<br/><b>Date:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}<br/><b>Clinician:</b> {clinician_name}", subtitle_style),
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=4, spaceAfter=10))

    # 2. Patient & Recording Metadata Table
    patient_id_val = getattr(report, "patient_identifier", "N/A")
    category_val = getattr(recording, "sound_category", "Heart").capitalize()
    location_val = getattr(recording, "chest_location", "Apex")
    duration_val = f"{getattr(recording, 'duration_seconds', 5.0):.1f} sec"
    gender_val = getattr(recording, "patient_gender", "Not Specified") or "Not Specified"
    age_val = str(getattr(recording, "patient_age", "N/A")) if getattr(recording, "patient_age", None) else "N/A"

    meta_data = [
        [
            Paragraph("<b>Patient Identifier:</b>", body_style), Paragraph(patient_id_val, body_style),
            Paragraph("<b>Sound Category:</b>", body_style), Paragraph(category_val, body_style),
        ],
        [
            Paragraph("<b>Patient Age / Gender:</b>", body_style), Paragraph(f"{age_val} / {gender_val}", body_style),
            Paragraph("<b>Chest Location:</b>", body_style), Paragraph(location_val, body_style),
        ],
        [
            Paragraph("<b>Recording Duration:</b>", body_style), Paragraph(duration_val, body_style),
            Paragraph("<b>Sample Rate:</b>", body_style), Paragraph(f"{getattr(recording, 'sample_rate', 4000)} Hz", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[120, 150, 120, 150])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. AI Screening Diagnostic Summary Box
    prediction_val = getattr(analysis, "predicted_class", "Normal")
    confidence_val = float(getattr(analysis, "confidence_score", 0.95))
    is_normal = "normal" in prediction_val.lower()
    status_label = "NORMAL FINDING" if is_normal else "ANOMALY DETECTED"

    diagnosis_box_data = [
        [
            Paragraph(f"<b>{status_label}</b>", badge_style),
            Paragraph(
                f"<b>Primary AI Diagnosis:</b> {prediction_val}<br/>"
                f"<b>Confidence Rating:</b> {confidence_val*100:.1f}% &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Model Version:</b> {getattr(analysis, 'model_version', 'v1.0.0')} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Inference Latency:</b> {getattr(analysis, 'inference_time_ms', 45.0):.1f} ms",
                body_style
            ),
        ]
    ]
    diag_table = Table(diagnosis_box_data, colWidths=[130, 410])
    diag_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), risk_color),
        ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#eff6ff") if is_normal else colors.HexColor("#fef2f2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 1, risk_color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(diag_table)
    story.append(Spacer(1, 10))

    # 4. Mel-Spectrogram & Grad-CAM Visual Explainability
    story.append(Paragraph("AI Explainability & Acoustic Spectrogram Analysis", heading_style))
    story.append(Paragraph(
        "The images below illustrate the frequency-domain Mel-Spectrogram (left) and the corresponding Grad-CAM Saliency Map (right). "
        "Warmer colors (red/orange) pinpoint the exact time-frequency acoustic regions that governed the neural network's diagnostic decision.",
        subtitle_style
    ))
    story.append(Spacer(1, 6))

    # Convert base64 spectrogram & Grad-CAM images to in-memory PIL/ReportLab images
    try:
        from app.services.ml_service import run_screening_inference
        # If paths are stored as base64 strings
        spec_bytes = None
        grad_bytes = None
        
        # Check if we can extract from analysis or re-generate
        if hasattr(recording, "file_path") and os.path.exists(recording.file_path):
            from app.services.audio_processing import preprocess_audio_pipeline
            pipe = preprocess_audio_pipeline(recording.file_path, target_sr=4000)
            spec_b64 = pipe["spectrogram_image"].split(",")[-1]
            spec_bytes = base64.b64decode(spec_b64)
            
            from app.services.ml_service import ModelLoader
            model = ModelLoader.get_instance().get_model(category_val.lower())
            tensor = pipe["spectrogram_array"][np.newaxis, :, :, np.newaxis]
            from app.services.gradcam import compute_gradcam, generate_gradcam_overlay
            hm = compute_gradcam(model, tensor)
            grad_b64 = generate_gradcam_overlay(pipe["spectrogram_array"], hm).split(",")[-1]
            grad_bytes = base64.b64decode(grad_b64)

        if spec_bytes and grad_bytes:
            img_spec = RLImage(io.BytesIO(spec_bytes), width=260, height=130)
            img_grad = RLImage(io.BytesIO(grad_bytes), width=260, height=130)
            img_table_data = [
                [Paragraph("<b>Log Mel-Spectrogram (20 Hz - 2000 Hz)</b>", body_style), Paragraph("<b>Grad-CAM Saliency Map Overlay</b>", body_style)],
                [img_spec, img_grad],
            ]
            img_table = Table(img_table_data, colWidths=[270, 270])
            img_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(img_table)
    except Exception as e:
        story.append(Paragraph(f"<i>[Spectrogram & Grad-CAM visual preview: {e}]</i>", subtitle_style))

    story.append(Spacer(1, 8))

    # 5. Clinical Findings & Plain-Language Explanation
    story.append(Paragraph("Clinical Findings & Plain-Language Explanation", heading_style))
    plain_explanation = get_clinical_explanation(category_val, prediction_val, "Normal" if is_normal else "Abnormal", confidence_val)
    story.append(Paragraph(plain_explanation, body_style))
    story.append(Spacer(1, 8))

    # 5b. Disease Progression & Associated Pathologies (if abnormal)
    progression_info = get_disease_progression_details(category_val, prediction_val, "Normal" if is_normal else "Abnormal")
    if progression_info.get("has_abnormality"):
        story.append(Paragraph("Associated Diseases & Clinical Progression Risks", heading_style))
        
        # Potential diseases list
        diseases_str = ", ".join(progression_info.get("potential_diseases", []))
        story.append(Paragraph(f"<b>Primary Clinical Correlation:</b> {progression_info.get('primary_condition')}", body_style))
        if diseases_str:
            story.append(Paragraph(f"<b>Differential Diagnoses:</b> {diseases_str}", body_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Progression Risk If Untreated:</b> {progression_info.get('progression_risks')}", body_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Urgency Rating:</b> {progression_info.get('urgency')}", body_style))
        story.append(Spacer(1, 8))

    # 6. Clinical Recommendations & Diagnostic Workup
    story.append(Paragraph("Recommended Diagnostic Workup & Next Steps", heading_style))
    workup_list = progression_info.get("recommended_workup", [])
    if workup_list:
        for item in workup_list:
            story.append(Paragraph(f"• {item}", body_style))
    else:
        recs = getattr(report, "recommendations", None)
        if not recs:
            recs = "No acute cardiopulmonary auscultation abnormalities identified. Continue routine clinical monitoring as indicated."
        for line in recs.split("\n"):
            if line.strip():
                story.append(Paragraph(f"• {line.strip()}", body_style))

    story.append(Spacer(1, 14))

    # 7. Disclaimer & Sign-off Footer
    footer_text = (
        "<b>CLINICAL DISCLAIMER:</b> This AI-generated screening report is intended solely as an assistive clinical decision support tool. "
        "It does not replace comprehensive medical evaluation, physical examination, or definitive diagnostic imaging by a licensed healthcare professional."
    )
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=6, spaceAfter=6))
    story.append(Paragraph(footer_text, subtitle_style))

    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
