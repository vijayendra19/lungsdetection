import io
import wave
import struct


def create_dummy_wav(duration_secs: float = 1.0) -> bytes:
    """Generates a valid mono PCM WAV in memory."""
    buf = io.BytesIO()
    sr = 4000
    total_samples = int(sr * duration_secs)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        samples = [int(1000 * struct.unpack("h", struct.pack("h", i % 1000))[0] / 1000) for i in range(total_samples)]
        packed = struct.pack(f"<{len(samples)}h", *samples)
        wf.writeframes(packed)
    return buf.getvalue()


def test_phase3_history_analysis_report_and_ownership(client):
    # 1. Register User A (Dr. Alice)
    reg_a = client.post(
        "/api/auth/register",
        json={"email": "alice@hospital.org", "password": "Password123!", "full_name": "Dr. Alice", "role": "clinician"},
    )
    assert reg_a.status_code == 201
    login_a = client.post("/api/auth/login", json={"email": "alice@hospital.org", "password": "Password123!"})
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B (Dr. Bob)
    reg_b = client.post(
        "/api/auth/register",
        json={"email": "bob@clinic.org", "password": "Password123!", "full_name": "Dr. Bob", "role": "clinician"},
    )
    assert reg_b.status_code == 201
    login_b = client.post("/api/auth/login", json={"email": "bob@clinic.org", "password": "Password123!"})
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User A uploads & analyzes a heart sound recording
    wav_bytes = create_dummy_wav(duration_secs=1.5)
    files = {"file": ("alice_heart_recording.wav", wav_bytes, "audio/wav")}
    data = {"sound_category": "heart", "chest_location": "Apex"}
    analyze_res_a = client.post("/api/audio/analyze", headers=headers_a, data=data, files=files)
    assert analyze_res_a.status_code == 200
    analysis_data_a = analyze_res_a.json()
    rec_id_a = analysis_data_a["recording_id"]

    # Fetch DB analysis ID
    db_ana_res = client.get(f"/api/analysis/by-recording/{rec_id_a}", headers=headers_a)
    assert db_ana_res.status_code == 200
    ana_id_a = db_ana_res.json()["id"]

    # 4. Test GET /api/history for User A
    history_a = client.get("/api/history/", headers=headers_a)
    assert history_a.status_code == 200
    hist_json = history_a.json()
    assert hist_json["total"] == 1
    item = hist_json["items"][0]
    assert item["recording_id"] == rec_id_a
    assert item["category"] == "heart"
    assert "prediction" in item
    assert "confidence" in item
    assert "date" in item

    # User B's history should be empty (0 items)
    history_b = client.get("/api/history/", headers=headers_b)
    assert history_b.status_code == 200
    assert history_b.json()["total"] == 0

    # 5. Test GET /api/analysis/{id} for User A
    detail_res_a = client.get(f"/api/analysis/{ana_id_a}", headers=headers_a)
    assert detail_res_a.status_code == 200
    detail = detail_res_a.json()
    assert detail["id"] == ana_id_a
    assert detail["category"] == "heart"
    assert detail["chest_location"] == "Apex"
    assert "waveform_data" in detail
    assert "spectrogram_image" in detail
    assert "gradcam_image" in detail
    assert "clinical_explanation" in detail
    assert len(detail["clinical_explanation"]) > 20

    # 6. Test Ownership Check: User B attempts to access User A's analysis -> 403 FORBIDDEN
    unauth_ana = client.get(f"/api/analysis/{ana_id_a}", headers=headers_b)
    assert unauth_ana.status_code == 403

    unauth_rec_ana = client.get(f"/api/analysis/by-recording/{rec_id_a}", headers=headers_b)
    assert unauth_rec_ana.status_code == 403

    # 7. User A generates a clinical report
    report_in = {
        "recording_id": rec_id_a,
        "analysis_id": ana_id_a,
        "report_title": "Cardiopulmonary Auscultation Summary",
        "patient_identifier": "PAT-7742",
        "primary_diagnosis": detail["prediction"],
        "severity": "normal",
        "clinical_summary": "",  # Auto-generates plain-language explanation
        "recommendations": "Routine follow-up in 12 months.",
        "status": "finalized",
    }
    create_rep_res = client.post("/api/report/generate", headers=headers_a, json=report_in)
    assert create_rep_res.status_code == 201
    report_id = create_rep_res.json()["id"]

    # 8. Test GET /api/report/{id} JSON representation
    rep_res_json = client.get(f"/api/report/{report_id}", headers=headers_a)
    assert rep_res_json.status_code == 200
    rep_data = rep_res_json.json()
    assert rep_data["patient_identifier"] == "PAT-7742"
    assert "clinical_explanation" in rep_data

    # 9. Test GET /api/report/{id} PDF Generation
    pdf_res = client.get(f"/api/report/{report_id}?format=pdf", headers=headers_a)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")  # Valid PDF header

    # Test direct /pdf route as well
    direct_pdf_res = client.get(f"/api/report/{report_id}/pdf", headers=headers_a)
    assert direct_pdf_res.status_code == 200
    assert direct_pdf_res.headers["content-type"] == "application/pdf"
    assert direct_pdf_res.content.startswith(b"%PDF-")

    # 10. Test Ownership Check: User B attempts to access User A's report -> 403 FORBIDDEN
    unauth_rep = client.get(f"/api/report/{report_id}", headers=headers_b)
    assert unauth_rep.status_code == 403

    unauth_pdf = client.get(f"/api/report/{report_id}/pdf", headers=headers_b)
    assert unauth_pdf.status_code == 403
