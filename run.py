from flask import Flask, jsonify
from app.routes.recipts import receipts_bp

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Service running", "status": "ok"})

app.register_blueprint(receipts_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
