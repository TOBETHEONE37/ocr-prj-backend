import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import openai
#from dotenv import load_dotenv

# 환경변수 불러오기
#load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

def translate_with_gpt(text: str) -> str:
    """GPT를 이용한 한자 → 한글 번역"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 전통 한의학 고서를 번역하는 한문 전문가입니다. 정확하고 자연스럽게 번역하세요."},
                {"role": "user", "content": f"다음 문장을 한글로 번역해줘:\n{text}"}
            ],
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[GPT 번역 오류]: {str(e)}"

@app.route('/')
def index():
    return jsonify({"status": "한의학 한자 OCR + 번역 API 정상 동작 중"})

@app.route('/upload', methods=['POST'])
def ocr_and_translate():
    if 'image' not in request.files:
        return jsonify({'error': 'Image is required.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No filename provided.'}), 400

    try:
        # OCR 모델 로딩 (lazy loading)
        reader = easyocr.Reader(['ch_tra'], gpu=False)

        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as tmp:
            file.save(tmp.name)
            result = reader.readtext(tmp.name, detail=0, paragraph=True)
            raw_text = '\n'.join(result)

            gpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "다음 한의학 한자 문장을 한글로 번역해줘."},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0.7
            )

            translated = gpt_response['choices'][0]['message']['content'].strip()

            return jsonify({'original': raw_text, 'translated': translated})

    except Exception as e:        
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
