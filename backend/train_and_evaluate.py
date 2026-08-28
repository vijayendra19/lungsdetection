import os
import glob
import json
import numpy as np
import pandas as pd
import scipy.signal
import librosa
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix
import keras
from keras import layers, models, optimizers

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Base dataset paths
DATASET_BASE = r'd:\New folder\HLS-CMDS Heart and Lung Sounds Dataset Recorded from a Clinical Manikin using Digital Stethoscope'
HS_CSV = os.path.join(DATASET_BASE, 'HS.csv')
LS_CSV = os.path.join(DATASET_BASE, 'LS.csv')
HS_DIR = os.path.join(DATASET_BASE, 'HS', 'HS')
LS_DIR = os.path.join(DATASET_BASE, 'LS', 'LS')

def preprocess_audio(file_path: str, target_sr: int = 4000, target_duration: float = 5.0):
    try:
        y, sr = librosa.load(file_path, sr=target_sr, mono=True)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

    # Butterworth bandpass 20Hz - 1800Hz
    nyq = 0.5 * target_sr
    b, a = scipy.signal.butter(4, [20.0 / nyq, min(1800.0, nyq - 50) / nyq], btype='band')
    y_filtered = scipy.signal.filtfilt(b, a, y)

    # Normalize
    max_amp = np.max(np.abs(y_filtered))
    if max_amp > 1e-6:
        y_filtered = (y_filtered - np.mean(y_filtered)) / max_amp

    # Segment / Pad to 5.0 seconds
    target_samples = int(target_sr * target_duration)
    if len(y_filtered) < target_samples:
        pad_width = target_samples - len(y_filtered)
        y_filtered = np.pad(y_filtered, (0, pad_width), mode='constant')
    else:
        y_filtered = y_filtered[:target_samples]

    # Compute Mel-Spectrogram (128 bands x 157 time frames)
    mel_spec = librosa.feature.melspectrogram(
        y=y_filtered,
        sr=target_sr,
        n_fft=512,
        hop_length=128,
        n_mels=128,
        fmin=20,
        fmax=min(2000, target_sr // 2)
    )
    log_mel = librosa.power_to_db(mel_spec, ref=np.max)
    log_mel = (log_mel - log_mel.min()) / (log_mel.max() - log_mel.min() + 1e-8)
    return log_mel

def build_cnn_model(input_shape=(128, 157, 1), num_classes=2):
    inputs = layers.Input(shape=input_shape, name="mel_spectrogram_input")
    x = layers.Conv2D(16, (3, 3), padding='same', activation='relu')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    x = layers.Conv2D(32, (3, 3), padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    
    x = layers.Conv2D(64, (3, 3), padding='same', activation='relu', name='conv2d_last')(x)
    x = layers.BatchNormalization()(x)
    x = layers.GlobalAveragePooling2D()(x)
    
    x = layers.Dense(64, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation='softmax', name='prediction_output')(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="stethoscope_cnn")
    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def train_and_eval_category(df_path, audio_dir, category_col, model_name):
    df = pd.read_csv(df_path)
    print(f"\n==================== Training & Evaluating on {model_name} ====================")
    print(f"Total samples: {len(df)}")
    print("Class distribution:\n", df[category_col].value_counts())

    X, y, labels = [], [], []
    unique_classes = sorted(df[category_col].unique())
    class_to_idx = {c: i for i, c in enumerate(unique_classes)}
    
    # Binary classification (Normal vs Abnormal)
    y_binary = []

    for _, row in df.iterrows():
        fname = f"{row.iloc[-1]}.wav"
        fpath = os.path.join(audio_dir, fname)
        if not os.path.exists(fpath):
            # Try alternate lookup
            matches = glob.glob(os.path.join(audio_dir, f"*{row.iloc[-1]}*.wav"))
            if matches:
                fpath = matches[0]
            else:
                continue

        spec = preprocess_audio(fpath)
        if spec is not None:
            X.append(spec)
            y.append(class_to_idx[row[category_col]])
            y_binary.append(0 if row[category_col].lower() == 'normal' else 1)
            labels.append(row[category_col])

    X = np.array(X)[..., np.newaxis]
    y = np.array(y)
    y_binary = np.array(y_binary)
    print(f"Loaded {len(X)} valid spectrograms with shape {X.shape}")

    # 1. Binary Screening (Normal vs Abnormal) 5-Fold Cross Validation
    print(f"\n--- 5-Fold Cross Validation: Binary Screening (Normal vs Abnormal) ---")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    binary_accs = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y_binary)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y_binary[train_idx], y_binary[val_idx]
        
        # Simple data augmentation (jitter)
        X_train_aug = np.concatenate([X_train, X_train + np.random.normal(0, 0.02, X_train.shape)], axis=0)
        y_train_aug = np.concatenate([y_train, y_train], axis=0)
        
        model = build_cnn_model(input_shape=X.shape[1:], num_classes=2)
        model.fit(X_train_aug, y_train_aug, epochs=25, batch_size=8, verbose=0)
        
        preds = np.argmax(model.predict(X_val, verbose=0), axis=1)
        acc = accuracy_score(y_val, preds)
        binary_accs.append(acc)
        print(f"Fold {fold+1} Accuracy: {acc*100:.2f}%")

    mean_binary_acc = np.mean(binary_accs)
    std_binary_acc = np.std(binary_accs)
    print(f">> Mean Binary Screening Accuracy: {mean_binary_acc*100:.2f}% ± {std_binary_acc*100:.2f}%")

    # 2. Multi-Class Classification (Train-Test Split 80/20)
    print(f"\n--- Multi-Class Classification ({len(unique_classes)} classes) ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y if min(pd.Series(y).value_counts()) >= 2 else None)
    
    X_train_aug = np.concatenate([X_train, X_train + np.random.normal(0, 0.015, X_train.shape)], axis=0)
    y_train_aug = np.concatenate([y_train, y_train], axis=0)

    mc_model = build_cnn_model(input_shape=X.shape[1:], num_classes=len(unique_classes))
    mc_model.fit(X_train_aug, y_train_aug, epochs=35, batch_size=8, verbose=0)
    
    test_preds = np.argmax(mc_model.predict(X_test, verbose=0), axis=1)
    test_acc = accuracy_score(y_test, test_preds)
    p, r, f1, _ = precision_recall_fscore_support(y_test, test_preds, average='weighted', zero_division=0)
    
    print(f">> Multi-Class Test Accuracy: {test_acc*100:.2f}%")
    print(f">> Weighted Precision: {p*100:.2f}%, Recall: {r*100:.2f}%, F1-Score: {f1*100:.2f}%")

    # Save trained weights for inference
    os.makedirs('app/services/saved_models', exist_ok=True)
    save_path = f'app/services/saved_models/{model_name.lower().replace(" ", "_")}.keras'
    mc_model.save(save_path)
    print(f"Saved trained model to: {save_path}")

    return {
        "dataset": model_name,
        "total_samples": len(X),
        "num_classes": len(unique_classes),
        "classes": unique_classes,
        "binary_accuracy_mean": mean_binary_acc,
        "binary_accuracy_std": std_binary_acc,
        "multiclass_accuracy": test_acc,
        "precision": p,
        "recall": r,
        "f1_score": f1
    }

if __name__ == '__main__':
    hs_results = train_and_eval_category(HS_CSV, HS_DIR, 'Heart Sound Type', 'Heart_Sounds')
    ls_results = train_and_eval_category(LS_CSV, LS_DIR, 'Lung Sound Type', 'Lung_Sounds')

    results = {
        "heart_sounds": hs_results,
        "lung_sounds": ls_results
    }
    with open('model_accuracy_metrics.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nTraining and evaluation complete! Metrics saved to model_accuracy_metrics.json")
