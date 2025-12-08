from flask import Flask, render_template, request, jsonify, url_for, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS
import tensorflow as tf
from preprocess import preprocess_image
import json
import csv

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
app = Flask(__name__)
CORS(app)

# Pastikan folder ini benar (di dalam folder static)
app.config['UPLOAD_FOLDER'] = 'static/uploads' 
app.config['PREDICTION_FOLDER'] = 'static/predictions'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PREDICTION_FOLDER'], exist_ok=True)

# --------------------------------------------------------
# LOAD MODEL
# --------------------------------------------------------
MODEL_PATH = "model/fer2013_mobilenetv2_final.h5"

print("Loading model...")
# Pastikan path model benar
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
else:
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

# --------------------------------------------------------
# ROUTES HALAMAN HTML
# --------------------------------------------------------

@app.route("/")
def home():
    testimonies = load_testimonies()
    return render_template("home.html", testimonies=testimonies)

@app.route('/about')
def about():
    return render_template('about.html') # Pastikan ada file about.html

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

# Route ini sebenarnya opsional sekarang, karena /predict langsung render result.html
@app.route('/result')
def result_page():
    return render_template('result.html')


# ROUTE TESTIMONY
def load_testimonies():
    testimonies = []
    with open("testimonies.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            testimonies.append(row)
    return testimonies

@app.route("/add_testimony", methods=["POST"])
def add_testimony():
    name = request.form["name"]
    msg = request.form["message"]

    with open("testimonies.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, msg])

    return redirect("/")

# --------------------------------------------------------
# ROUTE PREDICT (INTI PROGRAM)
# --------------------------------------------------------

@app.route('/predict', methods=['POST'])
def predict():
    # 1. Cek Input File
    # Pastikan di HTML <input name="image">. Jika name="file", ganti 'image' jadi 'file' di bawah ini.
    if 'image' not in request.files:
        return "Tidak ada gambar yang diunggah (Cek name input di HTML)", 400

    file = request.files['image']
    if file.filename == '':
        return "Nama file kosong", 400

    # 2. Simpan File
    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    
    file.save(filepath)

    # 3. Preprocessing & Prediksi
    try:
        img_array = preprocess_image(filepath)
        preds = model.predict(img_array)[0]

        emotion_index = preds.argmax()
        emotion = EMOTION_LABELS[emotion_index]
        confidence = float(preds[emotion_index])

        # 4. Siapkan Data Lengkap untuk Progress Bar
        # Dictionary: {'angry': 0.1, 'happy': 0.8, ...}
        all_predictions = {EMOTION_LABELS[i]: float(preds[i]) for i in range(7)}

        # (Opsional) Simpan JSON log history
        json_name = f"{uuid.uuid4().hex}.json"
        json_path = os.path.join(app.config['PREDICTION_FOLDER'], json_name)
        with open(json_path, "w") as f:
            json.dump({
                "emotion": emotion,
                "confidence": confidence,
                "all_predictions": all_predictions
            }, f, indent=4)

        # 5. Render Template (JANGAN HAPUS FOTO)
        # Kita kirim semua data yang dibutuhkan result.html
        return render_template(
            'result.html', 
            emotion=emotion, 
            confidence=confidence, 
            all_predictions=all_predictions, # <--- PENTING UNTUK BAR PERSENTASE
            image_url=url_for('static', filename=f'uploads/{filename}') # <--- PENTING UNTUK GAMBAR
        )

    except Exception as e:
        print(f"Error: {e}")
        return f"Terjadi kesalahan saat memproses gambar: {str(e)}", 500

# --------------------------------------------------------
# RUN SERVER
# --------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)