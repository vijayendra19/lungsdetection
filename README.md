# Smart Stethoscope AI 🩺⚡

> **Full-Stack Progressive Web App (PWA) for AI-Assisted Heart and Lung Sound Screening with Grad-CAM Visual Saliency Explainability.**

---

## 🌟 Overview & Architecture

**Smart Stethoscope AI** enables clinicians, researchers, and patients to upload or capture digital stethoscope audio (`.wav`), perform automated acoustic preprocessing, execute deep convolutional neural network (CNN) screening, inspect **Grad-CAM visual saliency heatmaps** overlaid on Mel-spectrograms, and generate downloadable **Clinical PDF Reports**.

```
┌─────────────────────────────────────────────────────────────┐
│  React + TypeScript PWA (Vite + Tailwind + Recharts)       │
│  - In-Browser Audio Recording (MediaRecorder + PCM WAV)     │
│  - Drag & Drop Audio Upload                                │
│  - Real-Time Waveform & Mel-Spectrogram Visualizer         │
│  - Interactive Grad-CAM Saliency Map Inspector             │
│  - Offline App Shell Caching (vite-plugin-pwa)             │
│  - Medical PDF Report Viewer & Export                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (Bearer JWT Auth)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend (Python 3.11+)                             │
│  - Authentication: JWT with Passlib/Bcrypt                  │
│  - Audio Preprocessing: SciPy Butterworth (20–1800 Hz)      │
│  - Feature Extraction: Librosa 128-band Mel-Spectrogram    │
│  - Inference Engine: TensorFlow/Keras CNN Classifier        │
│  - Explainability: Grad-CAM Saliency Gradient Saliency      │
│  - Clinical PDF Generator: ReportLab Engine                 │
│  - ORM & Migrations: SQLAlchemy 2.0 + Alembic               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL Database                                        │
│  - users, recordings, analyses, reports                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Monorepo Folder Structure

```
smart-stethoscope-ai/
├── README.md
│
├── dataset/                                   # HLS-CMDS Dataset
│   ├── HS/                                    # Heart Sound recordings & HS.csv
│   ├── LS/                                    # Lung Sound recordings & LS.csv
│   └── Mix/                                   # Mixed recordings & Mix.csv
│
├── backend/                                   # FastAPI Web Service
│   ├── app/
│   │   ├── main.py                            # FastAPI entrypoint, CORS, static routes
│   │   ├── config.py                          # Pydantic Settings & environment variables
│   │   ├── database.py                        # SQLAlchemy engine & session factory
│   │   ├── models/                            # SQLAlchemy ORM models (User, Recording, Analysis, Report)
│   │   ├── schemas/                           # Pydantic validation & response schemas
│   │   ├── api/                               # Modular REST API endpoints (auth, audio, analysis, history, report, health)
│   │   ├── core/                              # Bcrypt hashing & JWT token handlers
│   │   └── services/                          # Audio processing, ML loader, Grad-CAM, and ReportLab PDF generators
│   ├── alembic/                               # Database migration scripts
│   ├── tests/                                 # Pytest test suites (auth, audio, phase3, ownership)
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
└── frontend/                                  # React + TypeScript + Vite PWA
    ├── public/
    │   ├── icons/                             # PWA App icons (192x192, 512x512, maskable)
    │   └── manifest.webmanifest
    ├── src/
    │   ├── main.tsx                           # PWA Service Worker bootstrap
    │   ├── App.tsx                            # React Router configuration
    │   ├── context/                           # AuthContext with token refresh
    │   ├── services/                          # Axios API client with automatic token refresh
    │   ├── hooks/                             # useLiveAudioRecorder, usePWAInstall, useAuth
    │   ├── utils/                             # In-browser 16-bit PCM WAV encoder
    │   ├── types/                             # TypeScript definitions
    │   └── pages/                             # Login, Register, Dashboard, NewAnalysis, Result, History, Report
    ├── package.json
    ├── vite.config.ts                         # Vite + vite-plugin-pwa Workbox config
    └── tailwind.config.js
```

---

## ⚙️ Prerequisites

- **Python**: `3.11+` or `3.12`
- **Node.js**: `v18+` or `v20+` (and `npm v9+`)
- **PostgreSQL**: `v14+` (or SQLite fallback for quick prototyping)

---

## 🚀 Backend Setup & Execution

### 1. Navigate to the backend directory
```bash
cd backend
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and configure your database and JWT secret:
```ini
PROJECT_NAME="Smart Stethoscope AI Backend"
API_V1_STR="/api"
ENVIRONMENT="development"
DEBUG=True

# PostgreSQL Database URL
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/smart_stethoscope_db"
# (Or SQLite fallback for local testing without PostgreSQL: DATABASE_URL="sqlite:///./smart_stethoscope.db")

# JWT Security
JWT_SECRET="steth-ai-super-secret-key-change-in-production-123456789"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Upload Directories
UPLOAD_DIR="static/uploads"
HEATMAP_DIR="static/heatmaps"
```

### 5. Run Database Migrations
```bash
python -m alembic upgrade head
```

### 6. Run the Automated Test Suite
```bash
python -m pytest tests/ -v
```

### 7. Launch the FastAPI Development Server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **Alternative ReDoc**: [http://127.0.0.1:8000/api/redoc](http://127.0.0.1:8000/api/redoc)
- **Liveness Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 💻 Frontend Setup & Execution

### 1. Navigate to the frontend directory
```bash
cd frontend
```

### 2. Install Node Dependencies
```bash
npm install
```

### 3. Start the Frontend Vite Dev Server
```bash
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

### 4. Build for Production & PWA Service Worker
```bash
npm run build
```

---

## 📱 PWA Features & Offline Support

- **Progressive Web App**: Installable directly on Chrome Desktop, macOS/Windows, Android, and iOS Safari via the `"Install App"` button in the navigation bar.
- **Offline Shell Caching**: Application shell, layouts, CSS, icons, and bundles are pre-cached via Workbox Service Worker (`dist/sw.js`).
- **Live MediaRecorder Recording**: Capture real-time stethoscope auscultation audio directly inside the browser and auto-encode to 16-bit PCM WAV ($4000\text{ Hz}$).

---

## 🧪 AI & Explainability Pipeline

1. **Audio Preprocessing**:
   - **Bandpass Filtering**: 4th-order SciPy Butterworth filter ($20\text{ Hz} - 1800\text{ Hz}$) isolating cardiopulmonary acoustic signals.
   - **Noise Reduction**: Spectral gating with STFT subtraction.
   - **Mel-Spectrogram Generation**: 128-band Mel-frequency power spectrogram normalized and transformed to decibel scale.
2. **CNN Architecture & Model Loader**:
   - 2D Convolutional Neural Network with Residual/Conv blocks, Batch Normalization, and Softmax dense classification heads.
   - Modular `ModelLoader` dynamically loads trained weights (`.keras` / `.h5`) for Heart and Lung auscultation.
3. **Grad-CAM Saliency Explainability**:
   - Computes gradient activations of the predicted class score with respect to feature maps of `conv2d_last`.
   - Generates transparent Jet heatmaps overlaid directly on the Mel-spectrogram to pinpoint the exact frequency/time trigger of the diagnosis.
4. **Clinical Report Generation**:
   - Generates structured medical summaries with plain-language acoustic explanations.
   - Outputs printable, vector-rendered clinical PDF reports with embedded spectrograms and saliency maps.
