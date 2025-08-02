# app.py
from flask import Flask, render_template, request
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process image with OpenCV
        img = cv2.imread(filepath)
        img = cv2.resize(img, (500, 500))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v = hsv[:, :, 2]
        mean_brightness = np.mean(v)

        lower_brown = np.array([10, 100, 20])
        upper_brown = np.array([25, 255, 200])
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)

        brown_pixels = cv2.countNonZero(brown_mask)
        total_pixels = img.shape[0] * img.shape[1]
        brown_ratio = brown_pixels / total_pixels

        if brown_ratio < 0.05 or mean_brightness > 170:
            result = "❌ Not Cooked"
        elif 0.05 <= brown_ratio < 0.15:
            result = "🍳 Medium Cooked"
        elif 0.15 <= brown_ratio < 0.30:
            result = "✅ Perfectly Cooked"
        else:
            result = "🔥 Overcooked"

        return render_template('result.html', result=result, image=filename)

    return "No file uploaded."

if __name__ == '__main__':
    app.run(debug=True)
