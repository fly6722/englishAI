from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/correct", methods=["POST"])
def correct():
    data = request.json
    sentence = data.get("sentence")

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are an English teacher. Correct the grammar. Return only the corrected sentence."},
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
