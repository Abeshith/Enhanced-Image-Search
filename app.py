import pytesseract
from PIL import Image
import os
import sqlite3
import cv2
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def create_db():
    conn = sqlite3.connect('images.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS image_data (
                        id INTEGER PRIMARY KEY,
                        image_name TEXT,
                        text_content TEXT,
                        date TEXT,
                        category TEXT)''')
    conn.commit()
    conn.close()

def preprocess_image_opencv(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    # Resize for better DPI (~300)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    # Median blur to remove salt-and-pepper noise
    img = cv2.medianBlur(img, 3)
    # Adaptive thresholding for uneven lighting
    img = cv2.adaptiveThreshold(img, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    # Morphological opening (erosion + dilation) to clean small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    # Gaussian blur + Otsu threshold to smooth edges
    img = cv2.GaussianBlur(img, (5,5), 0)
    _, img = cv2.threshold(img, 0, 255,
                           cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img

def extract_text_from_image(image_path):
    processed = preprocess_image_opencv(image_path)
    pil_img = Image.fromarray(processed)
    config = r'--oem 1 --psm 6'  # LSTM OCR + single uniform block :contentReference[oaicite:1]{index=1}
    text = pytesseract.image_to_string(pil_img, config=config)
    print(f"Extracted Text: {text}")
    return text

def save_image_data(image_name, text, date, category):
    conn = sqlite3.connect('images.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO image_data (image_name, text_content, date, category) 
                      VALUES (?, ?, ?, ?)''', (image_name, text, date, category))
    conn.commit()
    conn.close()

def search_text(query):
    conn = sqlite3.connect('images.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM image_data WHERE text_content LIKE ?", ('%' + query.lower() + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['file']
    category = request.form['category']
    date = request.form['date']
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(image_path)
    
    text = extract_text_from_image(image_path)
    
    save_image_data(file.filename, text, date, category)
    
    return 'Image uploaded and text extracted!'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = search_text(query)
    print(f"Search Results: {results}")  # Debugging line
    if results:
        images = []
        for result in results:
            image_name = result[1]
            images.append(image_name)
        return render_template('results.html', images=images)
    else:
        return 'No results found.'

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    create_db()
    app.run(debug=True)
