from flask import Flask, request, jsonify
import psycopg2
import bcrypt
import jwt
import datetime
from werkzeug.exceptions import BadRequest
import os
from db_postgres import *
from kafka_producer import *
import logging

app = Flask(__name__)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Endpoint per la signup
@app.route('/signup', methods=['POST'])
def signup_route():
    try:
        data = request.get_json()  #JSON inviati nel body della richiesta

        # Estrai i dati
        username = data['username']
        password = data['password']
        image_url = data.get('image_url', '')  # URL dell'immagine (opzionale)

        # Registrazione utente
        signup(username, password, image_url)

        # Genera un token JWT
        token = generate_jwt_token(username, JWT_SECRET_KEY)

        # Risposta di successo
        return jsonify({'token': token, 'user': username, 'error': False, 'message': 'Signup successfully'}), 201

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid signup format'}), 400
    except BadRequest as e:
        return jsonify({'error': True, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Signup failed: {str(e)}'}), 500

# Endpoint per il login
@app.route('/login', methods=['POST'])
def login_route():
    try:
        data = request.get_json()

        username = data['username']
        password = data['password']

        user = login(username, password)

        # Invia un messaggio a Kafka
        notify_game_catalog(username)

        token = generate_jwt_token(username, JWT_SECRET_KEY)

        return jsonify({'token': token, 'user': username, 'error': False, 'message': 'Login successful'}), 200

    except BadRequest as e:
        return jsonify({'error': True, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Login failed: {str(e)}'}), 500

@app.route('/getUser/<string:username>', methods=['GET'])
def get_user_route(username):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        user = get_user(username)

        return jsonify({'user': user, 'error': False, 'message': 'User fetched successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get user format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get user failed: {str(e)}'}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3002)
