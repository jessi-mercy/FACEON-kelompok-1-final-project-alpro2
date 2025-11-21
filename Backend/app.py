# app.py
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from preprocess import preprocess_image

# ---------------------------------
# CONFIG & INIT
# ---------------------------------

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
PRED_FOLDER = "predictions"
MODEL_PATH = "model/emotion_model.h5"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PRED_FOLDER, exist_ok=True)

print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully.")


# Label emosi sesuai urutan output model
EMOTION_LABELS = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Sad",
    "Surprise",
    "Neutral"
]


# ---------------------------------
# TEST ROUTE
# ---------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Emotion Recognition API Running"})


# ---------------------------------
# PREDICT ROUTE
# ---------------------------------
@app.route("/predict", methods=["POST"])
def predict():

    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    img_file = request.files["image"]

    if img_file.filename == "":
        return jsonify({"error": "Empty file name"}), 400

    # Save uploaded image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"img_{timestamp}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    img_file.save(filepath)

    # Preprocess
    try:
        processed = preprocess_image(filepath)
    except Exception as e:
        return jsonify({"error": f"Preprocess error: {str(e)}"}), 500

    # Predict
    preds = model.predict(processed)[0].tolist()

    # Convert to dict with labels
    result = {EMOTION_LABELS[i]: float(preds[i]) for i in range(len(preds))}

    # Save JSON
    json_path = os.path.join(PRED_FOLDER, f"{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=4)

    return jsonify({
        "filename": filename,
        "timestamp": timestamp,
        "predictions": result
    })


# ---------------------------------
# RUN SERVER
# ---------------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
