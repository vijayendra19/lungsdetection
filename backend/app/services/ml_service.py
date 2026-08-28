import os
import time
from typing import Dict, Any, List, Optional
import numpy as np
import tensorflow as tf

from app.services.audio_processing import preprocess_audio_pipeline
from app.services.gradcam import compute_gradcam, generate_gradcam_overlay


# Class Label Mappings for Stethoscope Screening
CATEGORY_CLASSES = {
    "heart": [
        "Normal",
        "Mid Systolic Murmur",
        "Late Systolic Murmur",
        "Early Systolic Murmur",
        "Late Diastolic Murmur",
        "Atrial Fibrillation",
        "S3 Gallop",
        "S4 Gallop",
    ],
    "lung": [
        "Normal",
        "Wheezing",
        "Fine Crackles",
        "Coarse Crackles",
        "Rhonchi",
        "Pleural Rub",
    ],
    "mixed": [
        "Normal Cardiopulmonary",
        "Heart Murmur Present",
        "Adventitious Lung Sound",
        "Mixed Cardiopulmonary Abnormalities",
    ],
}


class ModelLoader:
    """
    Model Loading Abstraction.
    Loads real trained TensorFlow/Keras .keras/.h5 models if present on disk,
    or instantiates a compiled CNN architecture with a named last Conv2D layer for Grad-CAM.
    """
    _instance = None
    _models: Dict[str, tf.keras.Model] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._models = {}

    def _build_default_cnn(self, num_classes: int) -> tf.keras.Model:
        """Builds a lightweight 2D CNN model with residual/conv blocks and named target layer for Grad-CAM."""
        inputs = tf.keras.Input(shape=(128, None, 1), name="mel_spectrogram_input")
        
        # Block 1
        x = tf.keras.layers.Conv2D(32, (3, 3), padding="same", activation="relu", name="conv2d_1")(inputs)
        x = tf.keras.layers.BatchNormalization(name="bn_1")(x)
        x = tf.keras.layers.MaxPooling2D((2, 2), name="pool_1")(x)
        
        # Block 2
        x = tf.keras.layers.Conv2D(64, (3, 3), padding="same", activation="relu", name="conv2d_2")(x)
        x = tf.keras.layers.BatchNormalization(name="bn_2")(x)
        x = tf.keras.layers.MaxPooling2D((2, 2), name="pool_2")(x)
        
        # Block 3 (Target Conv Layer for Grad-CAM)
        x = tf.keras.layers.Conv2D(128, (3, 3), padding="same", activation="relu", name="conv2d_last")(x)
        x = tf.keras.layers.BatchNormalization(name="bn_3")(x)
        
        # Classification Head
        x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
        x = tf.keras.layers.Dense(64, activation="relu", name="dense_features")(x)
        outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="prediction_output")(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs, name="StethoscopeCNN")
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        return model

    def get_model(self, category: str = "heart") -> tf.keras.Model:
        """Retrieves or loads the CNN model for the given sound category."""
        category = category.lower()
        if category not in CATEGORY_CLASSES:
            category = "heart"

        if category in self._models:
            return self._models[category]

        classes = CATEGORY_CLASSES[category]
        num_classes = len(classes)

        # Check for pre-trained weights in standard locations
        model_paths = [
            os.path.join(os.path.dirname(__file__), "saved_models", f"{category}_sound_model.keras"),
            os.path.join("models", f"{category}_sound_model.keras"),
            os.path.join("..", "ml", "models", f"{category}_sound_model.keras"),
            os.path.join("app", "models", f"{category}_sound_model.keras"),
        ]

        loaded_model = None
        for path in model_paths:
            if os.path.exists(path):
                try:
                    loaded_model = tf.keras.models.load_model(path)
                    print(f"Loaded trained model from {path}")
                    break
                except Exception as e:
                    print(f"Notice: Failed loading model from {path}: {e}")

        if loaded_model is None:
            # Build default CNN
            loaded_model = self._build_default_cnn(num_classes)

        self._models[category] = loaded_model
        return loaded_model


def run_screening_inference(
    audio_path: str,
    category: str = "heart",
) -> Dict[str, Any]:
    """
    Executes end-to-end audio screening:
    1. Preprocessing (Bandpass filter, noise reduction, normalization, segmentation)
    2. Mel-Spectrogram & Downsampled Waveform generation
    3. CNN Model Inference (Classification, Confidence, Probabilities)
    4. Grad-CAM Saliency Map Generation
    """
    category = category.lower()
    if category not in CATEGORY_CLASSES:
        category = "heart"
    
    classes = CATEGORY_CLASSES[category]
    
    # 1. Preprocess Audio
    pipeline_result = preprocess_audio_pipeline(audio_path, target_sr=4000, target_duration=5.0)
    spec_array = pipeline_result["spectrogram_array"]  # Shape: (128, time_steps)
    
    # Format input tensor for CNN: (1, 128, time_steps, 1)
    input_tensor = spec_array[np.newaxis, :, :, np.newaxis]
    
    # 2. CNN Inference
    start_time = time.time()
    model_loader = ModelLoader.get_instance()
    model = model_loader.get_model(category)
    
    predictions = model(input_tensor, training=False).numpy()[0]
    inference_time_ms = round((time.time() - start_time) * 1000, 2)
    
    # Top predicted class
    predicted_idx = int(np.argmax(predictions))
    predicted_class = classes[predicted_idx]
    confidence_score = float(predictions[predicted_idx])
    
    # Classification: "Normal" or "Abnormal"
    classification = "Normal" if "normal" in predicted_class.lower() else "Abnormal"
    
    # Probabilities map
    class_probabilities = {
        cls_name: round(float(prob), 4) for cls_name, prob in zip(classes, predictions)
    }
    
    # 3. Grad-CAM Saliency Generation
    try:
        heatmap = compute_gradcam(
            model=model,
            input_tensor=input_tensor,
            last_conv_layer_name="conv2d_last",
            class_index=predicted_idx,
        )
        gradcam_image = generate_gradcam_overlay(
            spectrogram=spec_array,
            heatmap=heatmap,
            alpha=0.45,
            colormap_name="jet",
        )
    except Exception as e:
        print(f"Grad-CAM generation fallback: {e}")
        # Fallback to spectrogram image if Grad-CAM fails
        gradcam_image = pipeline_result["spectrogram_image"]

    return {
        "quality": pipeline_result["quality"],
        "category": category,
        "classification": classification,
        "prediction": predicted_class,
        "confidence": round(confidence_score, 4),
        "class_probabilities": class_probabilities,
        "waveform_data": pipeline_result["waveform_data"],
        "spectrogram_image": pipeline_result["spectrogram_image"],
        "gradcam_image": gradcam_image,
        "duration_seconds": pipeline_result["duration_seconds"],
        "sample_rate": pipeline_result["sample_rate"],
        "inference_time_ms": inference_time_ms,
    }
