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


def test_full_screening_pipeline(client):
    # 1. Register & Login Clinician
    reg = client.post(
        "/api/auth/register",
        json={
            "email": "cardiologist@clinic.com",
            "password": "StrongPassword123!",
            "full_name": "Dr. House",
            "role": "clinician",
        },
    )
    assert reg.status_code == 201

    login = client.post(
        "/api/auth/login",
        json={"email": "cardiologist@clinic.com", "password": "StrongPassword123!"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Audio File (.wav)
    wav_bytes = create_dummy_wav(duration_secs=2.0)
    files = {"file": ("test_heart_apex.wav", wav_bytes, "audio/wav")}
    data = {
        "sound_category": "heart",
        "chest_location": "Apex",
        "patient_gender": "M",
        "patient_age": "45",
        "clinical_notes": "Slight mid-systolic click noted during routine examination.",
    }
    upload_res = client.post("/api/audio/upload", headers=headers, data=data, files=files)
    assert upload_res.status_code == 201
    recording = upload_res.json()
    assert recording["sound_category"] == "heart"
    assert recording["chest_location"] == "Apex"
    assert recording["duration_seconds"] > 0
    recording_id = recording["id"]

    # 3. Retrieve Audio Details & Stream
    rec_res = client.get(f"/api/audio/{recording_id}", headers=headers)
    assert rec_res.status_code == 200
    assert rec_res.json()["id"] == recording_id

    stream_res = client.get(f"/api/audio/{recording_id}/file", headers=headers)
    assert stream_res.status_code == 200
    assert stream_res.headers["content-type"] == "audio/wav"

    # 4. Run AI Analysis via POST /api/audio/analyze using recording_id
    analyze_res = client.post(
        "/api/audio/analyze",
        headers=headers,
        data={"recording_id": recording_id},
    )
    assert analyze_res.status_code == 200
    analysis = analyze_res.json()
    assert analysis["recording_id"] == recording_id
    assert "quality" in analysis
    assert analysis["category"] == "heart"
    assert analysis["classification"] in ["Normal", "Abnormal"]
    assert "prediction" in analysis
    assert isinstance(analysis["confidence"], float)
    assert isinstance(analysis["waveform_data"], list)
    assert len(analysis["waveform_data"]) > 0
    assert analysis["spectrogram_image"].startswith("data:image/png;base64,")
    assert analysis["gradcam_image"].startswith("data:image/png;base64,")

    # 5. Run Direct File AI Analysis via POST /api/audio/analyze
    direct_wav_bytes = create_dummy_wav(duration_secs=1.5)
    direct_files = {"file": ("direct_lung_test.wav", direct_wav_bytes, "audio/wav")}
    direct_data = {"sound_category": "lung", "chest_location": "LUA"}
    direct_res = client.post("/api/audio/analyze", headers=headers, data=direct_data, files=direct_files)
    assert direct_res.status_code == 200
    direct_analysis = direct_res.json()
    assert direct_analysis["category"] == "lung"
    assert direct_analysis["spectrogram_image"].startswith("data:image/png;base64,")
    assert direct_analysis["gradcam_image"].startswith("data:image/png;base64,")

    # 6. Verify Persistence in analyses table via GET /api/analysis/{id} or by recording
    db_analysis_res = client.get(f"/api/analysis/by-recording/{recording_id}", headers=headers)
    assert db_analysis_res.status_code == 200
    persisted = db_analysis_res.json()
    assert persisted["recording_id"] == recording_id
    analysis_id = persisted["id"]

    # 7. Generate Clinical Report
    report_payload = {
        "recording_id": recording_id,
        "analysis_id": analysis_id,
        "report_title": "Cardiopulmonary Screening Report - Patient #1042",
        "patient_identifier": "PT-1042",
        "primary_diagnosis": analysis["prediction"],
        "severity": "mild",
        "clinical_summary": "Audio screening indicates heart sound acoustic features analyzed.",
        "recommendations": "Follow-up echocardiogram in 6 months if symptoms persist.",
        "status": "finalized",
    }
    report_res = client.post("/api/reports/generate", headers=headers, json=report_payload)
    assert report_res.status_code == 201
    report = report_res.json()
    assert report["patient_identifier"] == "PT-1042"
    assert report["status"] == "finalized"

    # 8. Check History and Stats
    history_res = client.get("/api/history/", headers=headers)
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert history_data["total"] == 2  # 1 from upload, 1 from direct analyze
