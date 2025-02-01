import pytesseract
from PIL import Image
import os
import sqlite3
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

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
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
