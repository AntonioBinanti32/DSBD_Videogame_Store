import os
from flask import Flask, jsonify, request, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from mongo_db import MongoDB
import jwt
import logging
from werkzeug.exceptions import BadRequest
import threading
from kafka_consumer import *

app = Flask(__name__)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

# Configurazione MongoDB dalle variabili d'ambiente
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "game-catalog")
MONGO_USER = os.getenv("MONGO_USER", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

# Connessione al database MongoDB
client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT,
    username=MONGO_USER if MONGO_USER else None,
    password=MONGO_PASSWORD if MONGO_PASSWORD else None,
)
db = client[MONGO_DB_NAME]
bcrypt = Bcrypt(app)

def verify_token(token, actual_user):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        if decoded_token.get('username') == actual_user:
            return True
        else:
            raise BadRequest('Invalid username in token')
    except jwt.ExpiredSignatureError:
        raise Exception("Token scaduto")
    except jwt.InvalidTokenError:
        raise Exception("Token non valido")

@app.route("/")
def home():
    return jsonify({"message": "Game Catalog Service is running!"})

@app.route("/getUserPreferredGames", methods=["GET"])
def handle_get_user_preferred_games():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not actual_user or not token:
            return jsonify({"error": True, "message":  "Invalid get user preferred games format"}), 400

        if not verify_token(token, actual_user):
            return jsonify({"error": True, "message": "Errore verifica del token"}), 403

        mongo_db = MongoDB.get_instance()
        games = mongo_db.get_user_preferred_games(actual_user)

        if not games:
            return jsonify({"message": "Nessun gioco preferito"}), 204

        return jsonify({"message": games}), 200

    except Exception as e:
        return jsonify({"message": f"Get user preferred games failed: {str(e)}"}), 500

if __name__ == "__main__":
    kafka_thread = threading.Thread(target=listen_for_user_registrations, daemon=True)
    kafka_thread.start()
    app.run(host="0.0.0.0", port=3001)
