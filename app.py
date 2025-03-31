from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import os
import tempfile

app = Flask(__name__)
CORS(app)  # 모든 출처 허용 (개발환경 추천)

# OCR 모델 초기화 (한국어, 한자 간체 모델)
reader = easyocr.Reader(['ko', 'ch_sim'], gpu=False)

@app.route('/upload', methods=['POST'])
def upload_and_process():
    # 업로드 파일 검증
    if 'image' not in request.files:
        return jsonify({'error': '이미지를 업로드해주세요.'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '파일이 없습니다.'}), 400

    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
        file.save(temp_img.name)
        
        # OCR 텍스트 추출
        result = reader.readtext(temp_img.name, detail=0, paragraph=True)

    # 임시 파일 삭제
    os.unlink(temp_img.name)

    # 결과 텍스트 반환
    extracted_text = '\n\n'.join(result)
    return jsonify({'text': extracted_text})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
