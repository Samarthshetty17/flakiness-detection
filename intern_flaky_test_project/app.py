import os
from flask import Flask, jsonify
from crew_app import run_crew

app = Flask(__name__)

@app.route("/")
def home():
    return "Flakiness Detection Web App Running 🚀"

@app.route("/analyze")
def analyze():
    try:
        result = run_crew()
        return jsonify({"result": str(result)})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))