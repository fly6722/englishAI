import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def home():
    return "AI English Practice Machine Running!"

@app.route("/practice", methods=["POST"])
def practice():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    audio_file = request.files["file"]

    # 🔹 存成暫存檔
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        audio_file.save(temp_audio.name)

        # 🔹 1️⃣ 語音轉文字
        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, open(temp_audio.name, "rb")),
            model="whisper-large-v3"
        )

    original_text = transcription.text.strip()

    # 🔹 2️⃣ 文法修正
    correction = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an English grammar correction teacher. Return JSON with keys: corrected and explanation."
            },
            {
                "role": "user",
                "content": f"Correct this sentence: {original_text}"
            }
        ],
        temperature=0.2
    )

    result_text = correction.choices[0].message.content

    return jsonify({
        "original": original_text,
        "result": result_text
    })

if __name__ == "__main__":
    app.run()
