import io
import base64
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def compute_gradcam(
    model: tf.keras.Model,
    input_tensor: np.ndarray,
    last_conv_layer_name: str = "conv2d_last",
    class_index: int = None,
) -> np.ndarray:
    """
    Calculates Grad-CAM saliency heatmap for the given input tensor and target class.
    input_tensor shape: (1, height, width, channels)
    """
    try:
        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(last_conv_layer_name).output, model.output],
        )
    except Exception:
        # If specific layer not found, find last Conv2D layer in model
        conv_layers = [l for l in model.layers if "conv" in l.name.lower()]
        if not conv_layers:
            # Fallback uniform heatmap if no conv layers
            return np.ones((input_tensor.shape[1], input_tensor.shape[2]), dtype=np.float32) * 0.5
        last_conv = conv_layers[-1]
        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[last_conv.output, model.output],
        )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(input_tensor)
        if class_index is None:
            class_index = int(tf.argmax(predictions[0]))
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    
    # Weight conv outputs by gradients
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    
    # ReLU on heatmap
    heatmap = tf.maximum(heatmap, 0.0)
    max_val = tf.math.reduce_max(heatmap)
    if max_val > 1e-8:
        heatmap = heatmap / max_val
    else:
        heatmap = tf.zeros_like(heatmap)
        
    return heatmap.numpy()


def generate_gradcam_overlay(
    spectrogram: np.ndarray,
    heatmap: np.ndarray,
    alpha: float = 0.45,
    colormap_name: str = "jet",
) -> str:
    """
    Overlays Grad-CAM heatmap on top of the Mel-Spectrogram and returns a Base64 PNG.
    """
    # Resize heatmap to match spectrogram dimensions (height, width)
    heatmap_resized = np.array(
        Image.fromarray(np.uint8(255 * heatmap)).resize(
            (spectrogram.shape[1], spectrogram.shape[0]),
            resample=Image.Resampling.BILINEAR,
        )
    ) / 255.0

    # Get colormaps
    spec_cm = plt.get_cmap("magma")
    heat_cm = plt.get_cmap(colormap_name)

    spec_colored = spec_cm(spectrogram)[:, :, :3]  # RGB
    heat_colored = heat_cm(heatmap_resized)[:, :, :3]  # RGB

    # Alpha blending
    # Give higher visibility where heatmap intensity is higher
    weight_map = heatmap_resized[:, :, np.newaxis] * alpha
    blended = (1.0 - weight_map) * spec_colored + weight_map * heat_colored
    blended = np.clip(blended, 0.0, 1.0)

    fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    ax.imshow(blended, origin="lower", aspect="auto")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    buf.seek(0)

    base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{base64_str}"
