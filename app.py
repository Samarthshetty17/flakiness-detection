import os
from flask import Flask, jsonify
from groq import Groq

app = Flask(__name__)

# Debug print
print("Starting Flask app...")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/")
def home():
    return "Flakiness Detection Web App is Running 🚀"

@app.route("/analyze")
def analyze():
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Analyze test flakiness"}]
        )
        result = response.choices[0].message.content
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Running on port {port}")
    app.run(host="0.0.0.0", port=port)