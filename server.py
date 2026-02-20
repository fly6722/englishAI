from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/correct", methods=["POST"])
def correct():
    data = request.json
    sentence = data.get("sentence")

    prompt = f"""
You are an English teacher.
Correct the grammar of this sentence.
Return only the corrected sentence.

Sentence:
{sentence}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    corrected = response.choices[0].message.content.strip()

    return jsonify({
        "original": sentence,
        "corrected": corrected
    })

@app.route("/")
def home():
    return "English AI Server Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
