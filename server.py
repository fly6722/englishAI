import os
import json
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# 讀取 Render 環境變數 (請確保您在 Render 介面已設定 GROQ_API_KEY)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# 首頁測試 (GET /)
# =========================
@app.route("/")
def home():
    return "AI English Practice Machine is Running!"

# =========================
# 1️⃣ 文字修正 API (POST /correct)
# 適合目前 ESP32 用 input() 輸入文字測試
# =========================
@app.route("/correct", methods=["POST"])
def correct():
    data = request.get_json()
    if not data or 'sentence' not in data:
        return jsonify({"error": "No sentence provided"}), 400
    
    user_text = data['sentence']
    
    try:
        # 使用 Llama 3.1 進行修正
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful English teacher. Return ONLY a JSON object with keys: 'corrected' (the corrected sentence) and 'explanation' (briefly explain why in Traditional Chinese)."
                },
                {
                    "role": "user", 
                    "content": f"Correct this sentence: {user_text}"
                }
            ],
            response_format={"type": "json_object"}
        )
        # 直接回傳 Groq 產生的 JSON 字串
        return completion.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# 2️⃣ 語音練習 API (POST /practice)
# 適合未來整合 INMP441 錄音上傳使用
# =========================
@app.route("/practice", methods=["POST"])
def practice():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]

    # 儲存暫存音檔
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        audio_file.save(temp_audio.name)

        # 1. Whisper 語音轉文字
        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, open(temp_audio.name, "rb")),
            model="whisper-large-v3"
        )

    original_text = transcription.text.strip()

    # 2. 文法修正
    correction = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system", 
                "content": "You are an English teacher. Return JSON with 'corrected' and 'explanation' (in Traditional Chinese)."
            },
            {
                "role": "user", 
                "content": f"Correct this sentence: {original_text}"
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return correction.choices[0].message.content

if __name__ == "__main__":
    # Render 會自動指定 PORT 環境變數
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
