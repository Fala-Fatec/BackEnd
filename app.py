import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Libera todas as rotas para qualquer origem
CORS(app)

# Caso queira restringir para origens específicas (ex: React rodando no localhost:3000):
# CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def home():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({"status": "sucesso", "message": "Conectado ao Supabase com sucesso!"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))