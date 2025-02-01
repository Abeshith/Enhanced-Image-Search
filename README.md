# Enhanced Image Search 📸📝

A Flask web app that lets users upload images, extract text via OCR, and store the data in a database. Users can categorize images, add metadata, and search the extracted text.

## Features ✨
- **Image Upload:** Upload images via the web interface.
- **Text Extraction:** Extract text from images using Tesseract OCR.
- **Metadata:** Store image category, date, and text in a database.
- **Search:** Search for images based on extracted text.
- **SQLite Database:** Save image data and metadata persistently.

## Tech Stack ⚙️
- **Flask**: Web framework for building the app.
- **Tesseract OCR**: For extracting text from images.
- **SQLite**: Database for storing metadata.

## How It Works 🔄
1. Upload an image 📤
2. Extract text using OCR 🔍
3. Store image data and text in the database 💾
4. Search for images by text 🖼️🔎

## Get Started 🚀
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the app: `python app.py`.
4. Visit `http://127.0.0.1:5000/` in your browser.

## Notes 📝
- Ensure **Tesseract OCR** is installed.
- Uploaded images are stored in the `uploads` folder.
- Data is saved in `images.db`.

