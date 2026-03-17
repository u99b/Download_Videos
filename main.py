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

NANO_API = "https://zecora0.serv00.net/ai/NanoBanana.php"
CHANNEL = "https://t.me/MITD6"
DEVELOPER = "@XVSJQ"

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
    except:
        return None


# ─── Chat ────────────────────────────────────────────────
@app.route("/")
def root():
    text = request.args.get("text", "")
    if text:
        result = ze(text)
        if result:
            return jsonify({"reply": result})
        return jsonify({"error": "no response"}), 500
    return jsonify({
        "status": "running",
        "channel": CHANNEL,
        "developer": DEVELOPER
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "missing message"}), 400
    result = ze(data["message"], data.get("model", "gemma-3-27b"))
    if result:
        return jsonify({"reply": result})
    return jsonify({"error": "no response"}), 500


# ─── Image Generation ────────────────────────────────────
@app.route("/image", methods=["POST"])
def image():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "missing text"}), 400

    payload = {
        "text": data["text"],
        "ratio": data.get("ratio", "1:1"),
        "res": data.get("res", "4K")
    }

    if "links" in data:
        payload["links"] = data["links"]

    try:
        r = requests.post(NANO_API, data=payload, timeout=60)
        result = r.json()
        result["channel"] = CHANNEL
        result["developer"] = DEVELOPER
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Image via GET ───────────────────────────────────────
@app.route("/image", methods=["GET"])
def image_get():
    text = request.args.get("text", "")
    if not text:
        return jsonify({"error": "missing text"}), 400

    payload = {
        "text": text,
        "ratio": request.args.get("ratio", "1:1"),
        "res": request.args.get("res", "4K")
    }

    try:
        r = requests.post(NANO_API, data=payload, timeout=60)
        result = r.json()
        result["channel"] = CHANNEL
        result["developer"] = DEVELOPER
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
