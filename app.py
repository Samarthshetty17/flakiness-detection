import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is working 🚀"

if __name__ == "__main__":
    print("Starting Flask server...")
    port = int(os.environ.get("PORT", 5000))
    print(f"Running on port {port}")
    app.run(host="0.0.0.0", port=port)