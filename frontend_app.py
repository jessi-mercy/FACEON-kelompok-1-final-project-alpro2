# frontend_app.py  (Laptop Frontend)
from flask import Flask, render_template, request, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Folder upload di FRONTEND (untuk ditampilkan di web)
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# GANTI IP INI dengan IP Laptop Predict di jaringan Wi-Fi
BACKEND_PREDICT_URL = "http://192.168.1.10:5000/predict"   # contoh


# --------------------- ROUTES HALAMAN --------------------


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/result")
def result_page():
    # route ini dipakai kalau kamu mau akses langsung, tapi
    # biasanya result dikirim dari /predict di bawah
    return render_template("result.html")


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
