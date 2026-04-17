import os
from flask import Flask, jsonify
from groq import Groq

app = Flask(__name__)

@app.route("/")
def home():
    return "Flakiness Detection Web App Running 🚀"

@app.route("/analyze")
def analyze():
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": "Analyze flaky test patterns"}
            ]
        )

        result = response.choices[0].message.content

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)