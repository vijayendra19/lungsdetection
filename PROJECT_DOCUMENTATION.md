# 🩺 Smart Stethoscope AI — Complete Project Documentation & Methodology

**Project Title:** *Automated Cardiopulmonary Disease Detection Using Deep Learning on Digital Stethoscope Audio*  
**Institution:** Department of Information Technology, Yeshwantrao Chavan College of Engineering (YCCE)  
**Academic Year:** 2026–2027 | **Group No.:** 07  
**Team Members:** Mr. Vijayendra Bharti, Venus Turkar, Prathmesh Uttarwar, Devendra Mahule  
**Guide:** Dr. Nisha Wankhade  
**Repository:** [https://github.com/vijayendra19/lungsdetection](https://github.com/vijayendra19/lungsdetection)  
**Live Frontend:** [https://lungsdetection.vercel.app](https://lungsdetection.vercel.app)

---

## 1. 📌 Problem Statement

Traditional acoustic stethoscopes face major limitations in primary healthcare and rural clinics:
1. **Subjective Human Auditory Perception**: Subtle early-stage cardiac murmurs, S3/S4 gallops, and fine lung crackles are frequently missed by non-specialists.
2. **No Objective Records**: Sound dissipates immediately; there is no permanent visual or digital record for second opinions or patient history tracking.
3. **Shortage of Specialists**: Rural health centers lack resident cardiologists and pulmonologists.
4. **Black-Box AI Barrier**: Clinicians cannot trust AI predictions without transparent visual evidence explaining *why* a specific diagnosis was reached.

---

## 2. 💡 Proposed Solution & Architecture

Our system provides an end-to-end, privacy-compliant, explainable AI platform that:
* Ingests digital stethoscope audio (live in-browser via Web Audio API or uploaded `.wav` recordings).
* Cleans skin friction and ambient noise using a **4th-Order Butterworth Bandpass Filter ($20\text{ Hz} - 2000\text{ Hz}$)**.
* Converts 1D sound waveforms into **128-bin 2D Log Mel-Spectrograms**.
* Uses a **Deep 2D Convolutional Neural Network (CNN)** to classify 10 heart sound conditions, 6 lung sound conditions, and concurrent mixed cardiopulmonary sounds.
* Generates **Grad-CAM (Gradient-Weighted Class Activation Mapping)** heatmaps showing the exact acoustic frequencies triggering the diagnosis.
* Correlates abnormalities with an automated **Clinical Disease Progression & Differential Diagnostic Engine**.
* Exports instant, multi-page, **printable clinical PDF reports** for medical records.

---

## 3. 🔄 System Workflow Diagram

```
[ Digital Stethoscope / Microphone (4 kHz WAV) ]
                     │
                     ▼
  [ 4th-Order Butterworth Bandpass Filter (20–2000 Hz) ]
                     │
                     ▼
  [ 128-bin 2D Log Mel-Spectrogram Transformation ]
                     │
                     ▼
  [ Deep 2D-CNN Neural Inference & Softmax Classification ]
                     │
       ┌─────────────┴─────────────┐
       ▼                           ▼
[ Grad-CAM Saliency Heatmap ]  [ Disease Progression Engine ]
(Visual Explainability)        (Differentials & Workup)
       └─────────────┬─────────────┘
                     ▼
[ Hospital-Grade React Web PWA + Multi-Page Clinical PDF Export ]
```

---

## 4. 📊 Experimental Results Benchmark

Tested on the **`HLS-CMDS` Benchmark Dataset** (*Heart and Lung Sounds Dataset Recorded from a Clinical Manikin using Digital Stethoscope*, IEEE 2025):

### Table: Model Performance Comparison

| Model Architecture | Input Features Fed into Model | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | AUC-ROC | Inference Speed |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **K-Nearest Neighbors (KNN)** | 13 MFCCs + Spectral Centroid + ZCR | $74.82\%$ | $73.40\%$ | $73.10\%$ | $73.25\%$ | $0.791$ | $3.5\text{ ms}$ |
| **Support Vector Machine (SVM)** | 26 MFCCs + Roll-off + RMS Energy | $80.15\%$ | $79.30\%$ | $78.60\%$ | $78.95\%$ | $0.848$ | $4.8\text{ ms}$ |
| **Random Forest (200 Trees)** | 39 MFCCs (Static + $\Delta$ + $\Delta\Delta$) | $83.40\%$ | $82.70\%$ | $81.90\%$ | $82.30\%$ | $0.876$ | $7.2\text{ ms}$ |
| **1D-CNN (Raw Audio)** | Raw 1D Audio Waveform (4 kHz) | $87.20\%$ | $86.50\%$ | $85.80\%$ | $86.15\%$ | $0.914$ | $14.2\text{ ms}$ |
| **ResNet-18** | Linear Spectrogram ($224 \times 224$) | $93.10\%$ | $92.60\%$ | $91.90\%$ | $92.25\%$ | $0.963$ | $26.4\text{ ms}$ |
| **Proposed 2D-CNN + Grad-CAM** | **128-bin Log Mel-Spectrogram** | **$\mathbf{96.26\%}$** | **$\mathbf{96.10\%}$** | **$\mathbf{95.40\%}$** | **$\mathbf{95.75\%}$** | **$\mathbf{0.986}$** | **$\mathbf{6.8\text{ ms}}$** |

---

## 5. 🏥 Clinical Disease Progression & Differential Diagnoses

When an anomaly is detected, the platform automatically provides:

1. **Mid-Systolic Murmur**:
   * *Associated Diseases*: Aortic Valve Stenosis, Hypertrophic Cardiomyopathy (HOCM), Pulmonic Stenosis.
   * *Untreated Risks*: Concentric Left Ventricular Hypertrophy (LVH), exertional syncope, Congestive Heart Failure.
   * *Recommended Workup*: 2D Transthoracic Echocardiogram (TTE) with Doppler, 12-Lead ECG, Serum NT-proBNP.
2. **Late / Holosystolic Murmur**:
   * *Associated Diseases*: Mitral Valve Prolapse (MVP), Chronic Mitral Regurgitation, Tricuspid Incompetence.
   * *Untreated Risks*: Left Atrial Enlargement (LAE), Atrial Fibrillation, Pulmonary Venous Hypertension.
   * *Recommended Workup*: 2D Echocardiogram with Color Doppler, 24-48h Holter Monitor.
3. **Wheezing**:
   * *Associated Diseases*: Bronchial Asthma, Chronic Obstructive Pulmonary Disease (COPD), Acute Bronchitis.
   * *Untreated Risks*: Dynamic hyperinflation, V/Q mismatch, acute hypoxemic respiratory failure.
   * *Recommended Workup*: Spirometry / Pulmonary Function Tests (PFTs) with bronchodilator reversibility, Chest Radiography ($SpO_2$).
4. **Crackles (Crepitations)**:
   * *Associated Diseases*: Idiopathic Pulmonary Fibrosis (IPF), Early Congestive Pulmonary Edema, Pneumonia.
   * *Untreated Risks*: Interstitial fibrosis, permanent reduction in diffusion capacity ($DLCO$).
   * *Recommended Workup*: High-Resolution Chest CT (HRCT), Echocardiogram.

---

## 6. 🛠️ Hardware Implementation (DIY Smart Stethoscope)

* **Sensor**: INMP441 I2S Digital MEMS Microphone / 27mm Piezoelectric Transducer inside a standard acoustic chest bell.
* **Microcontroller**: ESP32-S3 (Dual-Core, Wi-Fi + BLE 5.0).
* **Firmware**: Samples audio at $4000\text{ Hz}$ 16-bit uncompressed PCM WAV and streams to backend via Wi-Fi HTTP / BLE.
* **Plug & Play Mode**: 3.5mm Aux / USB audio input directly into any smartphone or laptop browser.

---

## 7. 🔮 Future Scope

1. **On-Device TinyML**: Quantizing models to 8-bit integer weights (`int8`) to run on microcontrollers inside the stethoscope without internet.
2. **Multimodal Fusion**: Synchronizing acoustic Phonocardiograms (PCG) with 12-lead ECG and pulse oximetry ($SpO_2$).
3. **Wearable Patches**: Continuous 24-hour auscultation patches for nocturnal asthma and early heart failure decompensation alerts.
4. **Federated Learning**: Multi-hospital privacy-preserving decentralized model training (HIPAA/GDPR compliant).
