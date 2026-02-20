from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import tempfile

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# 1️⃣ 語音轉文字 (STT)
# =========================
@app.route("/stt", methods=["POST"])
def speech_to_text():
    if "file" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["file"]

    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
        audio_file.save(temp_audio.name)

        transcription = client.audio.transcriptions.create(
            file=open(temp_audio.name, "rb"),
            model="whisper-large-v3"
        )

    return jsonify({
        "text": transcription.text
    })


# =========================
# 2️⃣ 文法修正 (LLM)
# =========================
@app.route("/correct", methods=["POST"])
def correct():
    data = request.json
    sentence = data.get("sentence")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "Return ONLY the corrected sentence. No explanation. No extra words."
            },
            {"role": "user", "content": sentence}
        ]
    )

    corrected = response.choices[0].message.content.strip()

    return jsonify({
        "original": sentence,
        "corrected": corrected
    })


@app.route("/")
def home():
    return "AI English Machine Backend Running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
