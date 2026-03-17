import requests
import re
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Linux; Android 10)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"
]

def ze(msg, model="gemma-3-27b"):
    try:
        r = requests.post(
            "https://gemma3.cc/api/chat",
            json={
                "model": model,
                "messages": [{"role": "user", "content": msg}]
            },
            headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Content-Type": "application/json"
            },
            timeout=30
        )
        if r.status_code == 200:
            text = "".join(re.findall(r'\d+:"([^"]*)"', r.text))
            text = text.replace("\\n", "\n").replace('\\"', '"')
            text = re.sub(r"\s+", " ", text)
            return text.strip()
        return None
    except Exception as e:
        return None

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "missing message"}), 400

    msg = data["message"]
    model = data.get("model", "gemma-3-27b")
    result = ze(msg, model)

    if result:
        return jsonify({"reply": result})
    return jsonify({"error": "no response"}), 500

@app.route("/")
def root():
    return jsonify({"status": "running"})
