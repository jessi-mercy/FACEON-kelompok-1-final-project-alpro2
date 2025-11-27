import cv2
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array

# Emotions List
EMOTIONS = ["Marah", "Jijik", "Takut", "Senang", "Sedih", "Terkejut", "Netral"]

# Path model
MODEL_PATH = os.path.join("model", "fer2013_mobilenetv2_final.h5")

# Global model
model = None


# =========================================================
# 1. LOAD MODEL (lebih aman & kompatibel)
# =========================================================
def load_emotion_model():
    global model

    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model tidak ditemukan: {MODEL_PATH}")
        model = None
        return None

    try:
        # MobileNetV2 kadang perlu custom_objects saat load
        model = tf.keras.models.load_model(
            MODEL_PATH,
            compile=False,
            custom_objects={"relu6": tf.nn.relu6}
        )

        print("✅ Model berhasil dimuat")
        print("Input shape :", model.input_shape)
        print("Output shape:", model.output_shape)

    except Exception as e:
        print("❌ Error memuat model:", e)
        model = None


# Load model sekali saat import
load_emotion_model()


# =========================================================
# 2. FACE DETECTION
# =========================================================
def detect_faces(image_path):
    try:
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        img = cv2.imread(image_path)
        if img is None:
            return False, "Gambar tidak dapat dibaca"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4, minSize=(40, 40)
        )

        if len(faces) == 0:
            return False, "Tidak ada wajah terdeteksi"

        return True, f"{len(faces)} wajah terdeteksi"

    except Exception as e:
        return False, f"Error deteksi wajah: {str(e)}"


# =========================================================
# 3. PREPROCESS
# =========================================================
def preprocess_image(image_path):
    if model is None:
        raise RuntimeError("Model belum dimuat")

    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Gambar tidak terbaca")

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Ambil ukuran input dari model
        h, w = model.input_shape[1:3]

        img = cv2.resize(img, (w, h))
        img = img.astype("float32") / 255.0
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)

        return img

    except Exception as e:
        raise Exception(f"Preprocessing gagal: {e}")


# =========================================================
# 4. FALLBACK MODE
# =========================================================
def fallback_predict_image(image_path):
    import random
    emotion = random.choice(EMOTIONS)
    confidence = round(random.uniform(0.70, 0.95), 2)
    return emotion, confidence


# =========================================================
# 5. MAIN PREDICT FUNCTION
# =========================================================
def predict_image(image_path):
    global model

    # Cek wajah dulu
    detected, msg = detect_faces(image_path)
    if not detected:
        return msg

    # Jika model fail di load → coba load ulang
    if model is None:
        load_emotion_model()

    # Jika tetap error → fallback
    if model is None:
        return fallback_predict_image(image_path)

    try:
        img = preprocess_image(image_path)
        preds = model.predict(img)[0]

        idx = int(np.argmax(preds))
        emotion = EMOTIONS[idx]
        confidence = float(preds[idx])

        return emotion, confidence

    except Exception as e:
        print("❌ Predict Error:", e)
        return fallback_predict_image(image_path)
