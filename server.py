from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/correct", methods=["POST"])
def correct():
    data = request.json
    sentence = data.get("sentence")

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an English teacher. Correct grammar only."},
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
    return "English AI Server Running (Groq)"

