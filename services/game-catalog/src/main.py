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
from kafka_producer import *

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

@app.route('/getGameByTitle/<string:title>', methods=['GET'])
def get_user_route(title):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        mongo_db = MongoDB.get_instance()
        game = mongo_db.get_game_by_title(title)
        return jsonify({'game': game, 'error': False, 'message': 'Gamed finded successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get game failed: {str(e)}'}), 500

@app.route('/addGame', methods=['POST'])
def add_game_route():
    try:

        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        data = request.get_json()

        title = data['title']
        genre = data['genre']
        release_date = data['releaseDate']
        developer = data['developer']
        price = data['price']
        stock = data['stock']
        description = data['description']
        image_url = data['imageUrl']

        mongo_db = MongoDB.get_instance()
        game = mongo_db.add_game(title, genre, release_date, developer, price, stock, description, image_url)
        if game:
            notify_order_service_add_game(title, stock, price)

            users = mongo_db.get_all_users()
            message = f"E' stato inserito nel catalogo un nuovo gioco: {title}. Vieni a scoprirlo!"
            notify_notification_service(users, message)

            return jsonify({'game': game, 'error': False, 'message': 'Gamed added successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Add game failed: {str(e)}'}), 500

@app.route('/updateGame', methods=['PUT'])
def update_game_route():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        data = request.get_json()

        updates = {}
        if 'title' in data:
            updates['title'] = data['title']
        if 'newGenre' in data:
            updates['genre'] = data['newGenre']
        if 'newReleaseDate' in data:
            updates['release_date'] = data['newReleaseDate']
        if 'newDeveloper' in data:
            updates['developer'] = data['newDeveloper']
        if 'newPrice' in data:
            updates['price'] = data['newPrice']
        if 'newStock' in data:
            updates['stock'] = data['newStock']
        if 'newDescription' in data:
            updates['description'] = data['newDescription']
        if 'newImageUrl' in data:
            updates['image_url'] = data['newImageUrl']

        if not updates:
            return jsonify({'error': True, 'message': 'No updates provided'}), 400

        mongo_db = MongoDB.get_instance()
        game = mongo_db.update_game(updates['title'], updates)

        notify_order_service_update_game(updates['title'], updates['stock'], updates['price'])

        return jsonify({'game': game, 'error': False, 'message': 'Gamed updated successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Update game failed: {str(e)}'}), 500

@app.route('/deleteGame/<string:title>', methods=['DELETE'])
def delete_game_route(title):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        mongo_db = MongoDB.get_instance()
        deleted = mongo_db.delete_game(title)
        if deleted:
            notify_order_service_delete_game(title)
            return jsonify({'error': False, 'message': f'Game {title} deleted successfully'}), 200
    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Delete game failed: {str(e)}'}), 500

@app.route('/addReview', methods=['POST'])
def add_review_route():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        data = request.get_json()

        username = data['username']
        game_title = data['gameTitle']
        review_text = data['reviewText']
        rating = data['rating']

        mongo_db = MongoDB.get_instance()
        review = mongo_db.add_review(username, game_title, review_text, rating)
        if review:
            message = f"L'utente {username} ha lasciato una recensione al gioco '{game_title}'"
            notify_notification_service_admin(message)
            return jsonify({'error': False, 'message': 'Review added successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Add game failed: {str(e)}'}), 500

@app.route('/getReviewByGame/<string:title>', methods=['GET'])
def get_review_by_game_route(title):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        mongo_db = MongoDB.get_instance()
        reviews = mongo_db.get_review_by_game(title)
        return jsonify({'reviews': reviews, 'error': False, 'message': 'Reviews finded successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get game failed: {str(e)}'}), 500

if __name__ == "__main__":
    kafka_thread = threading.Thread(target=listen_order_service, daemon=True)
    kafka_thread.start()
    app.run(host="0.0.0.0", port=3001, threaded=True)
