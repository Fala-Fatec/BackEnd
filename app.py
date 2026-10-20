from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import text

from config import Config
from errors import register_error_handlers
from extensions import db
from routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # acentos legíveis no JSON
    app.json.sort_keys = False

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    db.init_app(app)
    register_error_handlers(app)
    register_routes(app)

    @app.get("/")
    def home():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "sucesso", "message": "Conectado ao Supabase com sucesso!"}), 200
        except Exception as e:
            return jsonify({"status": "erro", "message": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    import os

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))