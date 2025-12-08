# backend_app.py  (Laptop Predict)
from flask import Flask, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import tensorflow as tf
from preprocess import preprocess_image  # pakai preprocess.py milikmu
import json

app = Flask(__name__)

# Folder lokal di Laptop Predict
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PREDICTION_FOLDER'] = 'predictions'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREDICTION_FOLDER'], exist_ok=True)

# --------------------- LOAD MODEL ------------------------
MODEL_PATH = "model/fer2013_mobilenetv2_final.h5"

print("Loading model on backend...")
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
else:
    model = None
    print(f"ERROR: Model file not found at {MODEL_PATH}")

EMOTION_LABELS = [
    "angry",
    "disgust",
    "fear",
    "happy",
    "neutral",
    "sad",
    "surprise"
]

# --------------------- ROUTES API ------------------------


@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


@app.route("/predict", methods=["POST"])
def predict():
    """
    Menerima file gambar (key: image atau file),
    mengembalikan JSON:
    {
        "emotion": "...",
        "confidence": 0.xx,
        "all_predictions": {...}
    }
    """
    # Cek apakah ada file
    file = request.files.get("image") or request.files.get("file")
    if file is None:
        return jsonify({"error": "Tidak ada file 'image' atau 'file' di request"}), 400

    if file.filename == "":
        return jsonify({"error": "Nama file kosong"}), 400

    # Simpan file ke folder uploads backend
    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"],
                            secure_filename(filename))
    file.save(filepath)

    # Prediksi
    if model is None:
        return jsonify({"error": "Model tidak ditemukan di server backend"}), 500

    try:
        img_array = preprocess_image(filepath)
        preds = model.predict(img_array)[0]

        emotion_index = int(preds.argmax())
        emotion = EMOTION_LABELS[emotion_index]
        confidence = float(preds[emotion_index])

        all_predictions = {
            EMOTION_LABELS[i]: float(preds[i])
            for i in range(len(EMOTION_LABELS))
        }

        # Simpan log JSON (opsional)
        json_name = f"{uuid.uuid4().hex}.json"
        json_path = os.path.join(app.config["PREDICTION_FOLDER"], json_name)

        with open(json_path, "w") as f:
            json.dump({
                "emotion": emotion,
                "confidence": confidence,
                "all_predictions": all_predictions,
                "image_filename": filename
            }, f, indent=4)

        # === HAPUS FILE GAMBAR & JSON SETELAH SELESAI ===
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(json_path):
                os.remove(json_path)
        except Exception as cleanup_err:
            # cuma print ke console biar tau kalau gagal hapus,
            # tapi jangan ganggu response ke client
            print("Gagal menghapus file:", cleanup_err)

        return jsonify({
            "emotion": emotion,
            "confidence": confidence,
            "all_predictions": all_predictions
        })

    except Exception as e:
        print("Error saat memproses gambar:", e)
        # kalau mau, di sini juga kamu bisa coba hapus filepath kalau sudah ada
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as cleanup_err:
            print("Gagal menghapus file setelah error:", cleanup_err)

        return jsonify({"error": f"Terjadi kesalahan saat memproses gambar: {str(e)}"}), 500

if __name__ == "__main__":
    # host=0.0.0.0 supaya bisa diakses dari laptop lain di jaringan Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)
