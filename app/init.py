from flask import Flask
from app.routes.recipts import receipts_bp
from app.utils.config import load_env

def create_app():
    load_env()
    app = Flask(__name__)
    app.register_blueprint(receipts_bp, url_prefix="/receipts")

    @app.route("/health")
    def health():
        return {"status": "ok", "message": "Service running"}
    return app
