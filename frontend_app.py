from flask import Flask, render_template, request, url_for, redirect
import os
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS
import requests
import csv

app = Flask(__name__)
CORS(app)

# Folder upload di FRONTEND (untuk ditampilkan di web)
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Nama file CSV untuk frontend
CSV_FILE = "testimonies.csv"

# GANTI IP INI dengan IP Laptop Predict di jaringan Wi-Fi
BACKEND_PREDICT_URL = "http://192.168.1.10:5000/predict"

# --------------------- FUNGSI BANTUAN CSV --------------------

def load_testimonies():
    """Membaca data testimoni dari CSV lokal di frontend"""
    testimonies = []
    
    if not os.path.exists(CSV_FILE):
        return []

    # Menggunakan utf-8-sig dan skipinitialspace agar data bersih
    with open(CSV_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            if row and row.get('name') and row.get('msg'):
                testimonies.append(row)
    return testimonies

# --------------------- ROUTES HALAMAN --------------------

@app.route("/")
def home():
    # Load testimoni agar tidak error di home.html
    testimonies = load_testimonies()
    return render_template("home.html", testimonies=testimonies)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/result")
def result_page():
    # Biasanya result ditampilkan via render_template di dalam fungsi predict
    return render_template("result.html")


# --------------------- ROUTE TESTIMONY (YANG HILANG) --------------------

@app.route("/add_testimony", methods=["POST"])
def add_testimony():
    """Menangani input testimoni dari form di home.html"""
    try:
        name = request.form["name"]
        msg = request.form["message"]

        # 1. Cek Enter di akhir file (supaya data tidak menempel)
        if os.path.exists(CSV_FILE) and os.stat(CSV_FILE).st_size > 0:
            with open(CSV_FILE, "r+", encoding="utf-8") as f:
                content = f.read()
                if not content.endswith('\n'):
                    f.write('\n')

        # 2. Cek Header
        file_exists = os.path.isfile(CSV_FILE)
        is_empty = False
        if file_exists:
            is_empty = os.stat(CSV_FILE).st_size == 0

        # 3. Tulis Data
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            fieldnames = ['name', 'msg']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists or is_empty:
                writer.writeheader()

            writer.writerow({'name': name, 'msg': msg})

        return redirect(url_for('home'))

    except Exception as e:
        print(f"Error saving testimony: {e}")
        return redirect(url_for('home'))


# --------------------- ROUTE PREDICT ---------------------

@app.route("/predict", methods=["POST"])
def predict():
    """
    1. Terima file dari form upload.
    2. Simpan ke static/uploads (frontend).
    3. Kirim file yang sama ke backend /predict.
    4. Terima JSON hasil prediksi dan render result.html.
    """
    file = request.files.get("image") or request.files.get("file")
    if file is None:
        return "Tidak ada gambar yang diunggah (cek name input di HTML)", 400

    if file.filename == "":
        return "Nama file kosong", 400

    # Simpan ke static/uploads
    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"],
                            secure_filename(filename))
    file.save(filepath)

    # Kirim ke backend
    try:
        with open(filepath, "rb") as f:
            files = {
                # key 'image' → disamakan dengan backend_app.py
                "image": (filename, f, file.mimetype)
            }
            resp = requests.post(BACKEND_PREDICT_URL,
                                files=files,
                                timeout=15)

        if resp.status_code != 200:
            return f"Backend error: {resp.text}", resp.status_code

        data = resp.json()
        emotion = data.get("emotion")
        confidence = data.get("confidence")
        all_predictions = data.get("all_predictions", {})

        image_url = url_for(
            "static", filename=f"uploads/{filename}", _external=False
        )

        return render_template(
            "result.html",
            emotion=emotion,
            confidence=confidence,
            all_predictions=all_predictions,
            image_url=image_url
        )

    except requests.exceptions.RequestException as e:
        print("Error komunikasi dengan backend:", e)
        return f"Gagal menghubungi server backend: {str(e)}", 500


if __name__ == "__main__":
    # Bisa diakses dari device lain di jaringan yang sama
    app.run(host="0.0.0.0", port=8000, debug=True)