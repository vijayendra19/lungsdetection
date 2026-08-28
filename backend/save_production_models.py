import os
import json
import joblib
import librosa
import scipy.signal
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler

BASE_DIR = r'd:\New folder\HLS-CMDS Heart and Lung Sounds Dataset Recorded from a Clinical Manikin using Digital Stethoscope'
OUTPUT_DIR = r'd:\New folder\backend\app\services\saved_models'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_features(fpath):
    y, sr = librosa.load(fpath, sr=4000)
    nyq = 0.5 * sr
    b, a = scipy.signal.butter(4, [20.0 / nyq, 1800.0 / nyq], btype='band')
    y = scipy.signal.filtfilt(b, a, y)
    
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40)
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y)
    rms = librosa.feature.rms(y=y)
    
    return np.hstack([
        np.mean(mfcc, axis=1), np.std(mfcc, axis=1),
        np.mean(mel, axis=1), np.std(mel, axis=1),
        np.mean(spec_cent), np.std(spec_cent),
        np.mean(spec_bw), np.std(spec_bw),
        np.mean(zcr), np.std(zcr),
        np.mean(rms), np.std(rms)
    ])

def train_and_save():
    print("Training and serializing production models...")
    
    # 1. Heart Sounds Model
    hs_df = pd.read_csv(os.path.join(BASE_DIR, 'HS.csv'))
    X_hs, y_hs, y_hs_bin = [], [], []
    for _, r in hs_df.iterrows():
        fpath = os.path.join(BASE_DIR, 'HS', 'HS', f"{r.iloc[-1]}.wav")
        if os.path.exists(fpath):
            X_hs.append(extract_features(fpath))
            y_hs.append(r['Heart Sound Type'])
            y_hs_bin.append('Normal' if r['Heart Sound Type'].lower() == 'normal' else 'Abnormal')
            
    X_hs = np.array(X_hs)
    scaler_hs = StandardScaler()
    X_hs_scaled = scaler_hs.fit_transform(X_hs)
    
    hs_classes = sorted(list(set(y_hs)))
    hs_model = RandomForestClassifier(n_estimators=200, random_state=42)
    hs_model.fit(X_hs_scaled, y_hs)
    
    joblib.dump(hs_model, os.path.join(OUTPUT_DIR, 'heart_sound_model.joblib'))
    joblib.dump(scaler_hs, os.path.join(OUTPUT_DIR, 'heart_sound_scaler.joblib'))
    with open(os.path.join(OUTPUT_DIR, 'heart_sound_classes.json'), 'w') as f:
        json.dump(hs_classes, f, indent=2)
    print(f"Saved Heart Sounds Model ({len(hs_classes)} classes)")

    # 2. Lung Sounds Model
    ls_df = pd.read_csv(os.path.join(BASE_DIR, 'LS.csv'))
    X_ls, y_ls = [], []
    for _, r in ls_df.iterrows():
        fpath = os.path.join(BASE_DIR, 'LS', 'LS', f"{r.iloc[-1]}.wav")
        if os.path.exists(fpath):
            X_ls.append(extract_features(fpath))
            y_ls.append(r['Lung Sound Type'])
            
    X_ls = np.array(X_ls)
    scaler_ls = StandardScaler()
    X_ls_scaled = scaler_ls.fit_transform(X_ls)
    
    ls_classes = sorted(list(set(y_ls)))
    ls_model = SVC(kernel='rbf', C=10.0, probability=True, random_state=42)
    ls_model.fit(X_ls_scaled, y_ls)
    
    joblib.dump(ls_model, os.path.join(OUTPUT_DIR, 'lung_sound_model.joblib'))
    joblib.dump(scaler_ls, os.path.join(OUTPUT_DIR, 'lung_sound_scaler.joblib'))
    with open(os.path.join(OUTPUT_DIR, 'lung_sound_classes.json'), 'w') as f:
        json.dump(ls_classes, f, indent=2)
    print(f"Saved Lung Sounds Model ({len(ls_classes)} classes)")

    # 3. Overall Binary Screening Model (Heart + Lung pooled)
    X_all = np.vstack([X_hs, X_ls])
    y_all_bin = ['Normal' if y.lower() == 'normal' else 'Abnormal' for y in y_hs + y_ls]
    scaler_all = StandardScaler()
    X_all_scaled = scaler_all.fit_transform(X_all)
    
    bin_model = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=600, random_state=42)
    bin_model.fit(X_all_scaled, y_all_bin)
    
    joblib.dump(bin_model, os.path.join(OUTPUT_DIR, 'binary_screening_model.joblib'))
    joblib.dump(scaler_all, os.path.join(OUTPUT_DIR, 'screening_scaler.joblib'))
    print(f"Saved Overall Binary Screening Model (Pooled dataset)")

    # Metadata manifest
    manifest = {
        "heart_sound_model": {
            "file": "heart_sound_model.joblib",
            "classes": hs_classes,
            "samples_trained": len(X_hs)
        },
        "lung_sound_model": {
            "file": "lung_sound_model.joblib",
            "classes": ls_classes,
            "samples_trained": len(X_ls)
        },
        "binary_screening_model": {
            "file": "binary_screening_model.joblib",
            "classes": ["Normal", "Abnormal"],
            "samples_trained": len(X_all)
        }
    }
    with open(os.path.join(OUTPUT_DIR, 'model_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"Successfully saved all models and manifest to: {OUTPUT_DIR}")

if __name__ == '__main__':
    train_and_save()
