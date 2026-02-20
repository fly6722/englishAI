import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# 讀取 Render 環境變數
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# 首頁測試
# =========================
@app.route("/")
def home():
    return "AI English Practice Machine Running!"

# =========================
# 語音練習整合 API
# =========================
@app.route("/practice", methods=["POST"])
def practice():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]

    # 儲存暫存音檔（Groq 需要實體檔案）
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        audio_file.save(temp_audio.name)

        # 1️⃣ Whisper 語音轉文字
        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, open(temp_audio.name, "rb")),
            model="whisper-large-v3"
        )

    original_text = transcription.text.strip()

    # 2️⃣ LLM 文法修正
    correction = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Return JSON with keys: corrected and explanation."
            },
            {
                "role": "user",
                "content": f"Correct this sentence: {original_text}"
            }
        ]
    )

    result_text = correction.choices[0].message.content.strip()

    return jsonify({
        "original": original_text,
        "result": result_text
    })
