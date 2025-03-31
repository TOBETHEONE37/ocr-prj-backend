import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import tempfile

app = Flask(__name__)
CORS(app)

reader = easyocr.Reader(['ko', 'ch_sim'], gpu=False)

@app.route('/')
def home():
    return jsonify({"status": "Railway OCR API Running!"})

@app.route('/upload', methods=['POST'])
def upload_and_process():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename.'}), 400

    with tempfile.NamedTemporaryFile(delete=True, suffix='.png') as temp_img:
        file.save(temp_img.name)
        result = reader.readtext(temp_img.name, detail=0, paragraph=True)

    extracted_text = '\n\n'.join(result)
    return jsonify({'text': extracted_text})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
