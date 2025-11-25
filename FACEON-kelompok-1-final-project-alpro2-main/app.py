from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from predict import predict_image, fallback_predict_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/result')
def result_page():
    emotion = request.args.get('emotion', 'Tidak Dikenali')
    confidence = request.args.get('confidence', '0')
    return render_template('result.html', emotion=emotion, confidence=confidence)

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada gambar yang diunggah'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nama file kosong'}), 400

    # Save uploaded file
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    try:
        # Try to predict with main model
        result = predict_image(path)
    except Exception as e:
        # Clean up file if prediction fails
        if os.path.exists(path):
            os.remove(path)
        return jsonify({'error': f'Prediksi gagal: {str(e)}'}), 500

    # Clean up uploaded file after prediction
    if os.path.exists(path):
        os.remove(path)

    # Handle different result formats
    if isinstance(result, tuple):
        if len(result) == 3:
            label, confidence, annotated_image = result
            return jsonify({
                'emotion': label,
                'confidence': round(confidence, 2),
                'image_url': annotated_image
            })
        else:
            label, confidence = result
            return jsonify({
                'emotion': label, 
                'confidence': round(confidence, 2)
            })

    # If result is string (error), try fallback
    if isinstance(result, str):
        # Try fallback prediction
        try:
            fallback_result = fallback_predict_image(path)
            if isinstance(fallback_result, tuple):
                label, confidence = fallback_result
                return jsonify({
                    'emotion': label, 
                    'confidence': round(confidence, 2)
                })
            else:
                return jsonify({'error': fallback_result}), 200
        except Exception as fallback_error:
            return jsonify({'error': f'Kedua prediksi gagal: {str(fallback_error)}'}), 500

    return jsonify({'error': 'Format hasil prediksi tidak diharapkan'}), 500

if __name__ == '__main__':
    app.run(debug=True)