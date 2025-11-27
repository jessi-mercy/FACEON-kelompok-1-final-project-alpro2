import cv2
import numpy as np

def preprocess_image(path):
    """
    Load image, convert to RGB, resize to 48x48, normalize, and expand dims.
    """
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Gambar tidak bisa dibaca.")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (48, 48))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)  # shape: (1,48,48,3)
    return img
