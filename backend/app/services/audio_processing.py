import io
import base64
import numpy as np
import scipy.signal
import librosa
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def load_audio(file_path: str, target_sr: int = 4000) -> tuple[np.ndarray, int]:
    """Loads an audio file and resamples it to target sample rate."""
    try:
        y, sr = librosa.load(file_path, sr=target_sr, mono=True)
    except Exception:
        # Fallback to soundfile then resample
        y, sr = sf.read(file_path)
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        if sr != target_sr:
            y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
            sr = target_sr
    return y.astype(np.float32), sr


def bandpass_filter(
    audio: np.ndarray,
    lowcut: float = 20.0,
    highcut: float = 1800.0,
    sr: int = 4000,
    order: int = 4,
) -> np.ndarray:
    """Applies a Butterworth bandpass filter to focus on heart/lung acoustic frequencies."""
    nyquist = 0.5 * sr
    low = max(0.001, lowcut / nyquist)
    high = min(0.999, highcut / nyquist)
    b, a = scipy.signal.butter(order, [low, high], btype="bandpass")
    filtered_audio = scipy.signal.filtfilt(b, a, audio)
    return filtered_audio.astype(np.float32)


def normalize_audio(audio: np.ndarray) -> np.ndarray:
    """Normalizes audio signal to [-1.0, 1.0] with peak and RMS scaling."""
    peak = np.max(np.abs(audio))
    if peak > 1e-6:
        audio = audio / peak
    # Remove DC offset
    audio = audio - np.mean(audio)
    return audio.astype(np.float32)


def reduce_noise(audio: np.ndarray, sr: int = 4000) -> np.ndarray:
    """Applies spectral noise reduction by estimating stationary background noise."""
    # Compute STFT
    stft = librosa.stft(audio, n_fft=512, hop_length=128)
    magnitude, phase = librosa.magphase(stft)
    
    # Estimate noise threshold from lowest energy frames (first 10% or minimum 5 frames)
    n_frames = magnitude.shape[1]
    noise_frames = max(3, int(n_frames * 0.1))
    noise_profile = np.median(magnitude[:, :noise_frames], axis=1, keepdims=True)
    
    # Spectral subtraction with floor
    cleaned_mag = np.maximum(magnitude - 1.2 * noise_profile, 0.05 * magnitude)
    
    # Reconstruct audio
    cleaned_stft = cleaned_mag * phase
    cleaned_audio = librosa.istft(cleaned_stft, hop_length=128, length=len(audio))
    return cleaned_audio.astype(np.float32)


def segment_or_pad(audio: np.ndarray, sr: int = 4000, target_duration: float = 5.0) -> np.ndarray:
    """Pads or center-crops audio to a fixed duration."""
    target_samples = int(sr * target_duration)
    if len(audio) < target_samples:
        # Repeat or zero pad
        pad_width = target_samples - len(audio)
        audio = np.pad(audio, (0, pad_width), mode="constant")
    elif len(audio) > target_samples:
        start = (len(audio) - target_samples) // 2
        audio = audio[start : start + target_samples]
    return audio


def assess_audio_quality(audio: np.ndarray, sr: int = 4000) -> str:
    """Estimates Signal-to-Noise Ratio (SNR) and clipping artifacts."""
    if len(audio) == 0:
        return "Unusable (Empty)"
    
    # Clipping detection
    clipping_ratio = np.sum(np.abs(audio) >= 0.99) / float(len(audio))
    if clipping_ratio > 0.05:
        return f"Warning: Severe Clipping Detected ({clipping_ratio*100:.1f}%)"
    
    # SNR Estimation
    signal_power = np.mean(audio ** 2)
    # High frequency residual power as noise estimate (> 1500 Hz)
    nyquist = 0.5 * sr
    b, a = scipy.signal.butter(4, min(0.99, 1500.0 / nyquist), btype="highpass")
    noise = scipy.signal.filtfilt(b, a, audio)
    noise_power = max(1e-9, np.mean(noise ** 2))
    
    snr_db = 10 * np.log10(max(1e-9, signal_power) / noise_power)
    
    if snr_db > 18.0:
        return f"Good (SNR: {snr_db:.1f} dB)"
    elif snr_db > 10.0:
        return f"Acceptable (SNR: {snr_db:.1f} dB)"
    else:
        return f"Low SNR ({snr_db:.1f} dB) - Potential Ambient Noise"


def extract_waveform_downsampled(audio: np.ndarray, max_points: int = 250) -> list[float]:
    """Downsamples audio waveform for frontend Recharts / Canvas display."""
    if len(audio) <= max_points:
        return [round(float(x), 4) for x in audio]
    
    step = len(audio) / float(max_points)
    downsampled = []
    for i in range(max_points):
        start = int(i * step)
        end = int((i + 1) * step)
        chunk = audio[start:end]
        if len(chunk) > 0:
            # Pick max magnitude sample in chunk to preserve peaks
            idx = np.argmax(np.abs(chunk))
            downsampled.append(round(float(chunk[idx]), 4))
        else:
            downsampled.append(0.0)
    return downsampled


def generate_mel_spectrogram(
    audio: np.ndarray,
    sr: int = 4000,
    n_mels: int = 128,
    n_fft: int = 512,
    hop_length: int = 128,
    fmin: float = 20.0,
    fmax: float = 2000.0,
) -> tuple[np.ndarray, str]:
    """
    Computes Log Mel-Spectrogram and renders it as a Base64-encoded PNG image.
    Returns: (normalized_spectrogram_array, base64_image_uri)
    """
    mel_spec = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_mels=n_mels,
        n_fft=n_fft,
        hop_length=hop_length,
        fmin=fmin,
        fmax=fmax,
        power=2.0,
    )
    # Convert to decibels
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Normalize to [0, 1] range for CNN model
    spec_min, spec_max = mel_spec_db.min(), mel_spec_db.max()
    if spec_max - spec_min > 1e-6:
        normalized_spec = (mel_spec_db - spec_min) / (spec_max - spec_min)
    else:
        normalized_spec = np.zeros_like(mel_spec_db)
    
    # Render PNG image in memory using matplotlib viridis colormap
    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    ax.imshow(normalized_spec, origin="lower", aspect="auto", cmap="magma")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    
    base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    base64_image = f"data:image/png;base64,{base64_str}"
    
    return normalized_spec.astype(np.float32), base64_image


def preprocess_audio_pipeline(
    file_path: str,
    target_sr: int = 4000,
    target_duration: float = 5.0,
) -> dict:
    """Full preprocessing pipeline execution."""
    raw_audio, sr = load_audio(file_path, target_sr=target_sr)
    quality = assess_audio_quality(raw_audio, sr=sr)
    
    # Filter & Denoise
    filtered = bandpass_filter(raw_audio, lowcut=20.0, highcut=1800.0, sr=sr)
    denoised = reduce_noise(filtered, sr=sr)
    normalized = normalize_audio(denoised)
    standardized = segment_or_pad(normalized, sr=sr, target_duration=target_duration)
    
    waveform = extract_waveform_downsampled(standardized, max_points=250)
    spec_array, spec_image = generate_mel_spectrogram(standardized, sr=sr)
    
    return {
        "raw_audio": raw_audio,
        "processed_audio": standardized,
        "sample_rate": sr,
        "duration_seconds": len(raw_audio) / float(sr),
        "quality": quality,
        "waveform_data": waveform,
        "spectrogram_array": spec_array,
        "spectrogram_image": spec_image,
    }
