from flask import Flask, request, jsonify
import psycopg2
import bcrypt
import jwt
import datetime
from werkzeug.exceptions import BadRequest
import os
import threading

from db_postgres import *
from kafka_producer import *
from kafka_consumer import *
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

@app.route("/")
def home():
    return jsonify({"message": "Order Service is running!"})

# Endpoint per la signup
@app.route('/signup', methods=['POST'])
def signup_route():
    try:
        data = request.get_json()

        username = data['username']
        password = data['password']
        image_url = data.get('image_url', '')

        signup(username, password, image_url)

        notify_game_catalog_signup(username)

        token = generate_jwt_token(username, JWT_SECRET_KEY)

        return jsonify({'token': token, 'user': username, 'error': False, 'message': 'Signup successfully'}), 200

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

@app.route('/getReservations/<string:username>', methods=['GET'])
def get_reservations_route(username):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        reservations = get_reservations(username)

        return jsonify({'reservations': reservations, 'error': False, 'message': 'User fetched successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get reservation format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get reservation failed: {str(e)}'}), 500

@app.route('/addReservation', methods=['POST'])
def add_reservation_route():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        data = request.get_json()

        username = data['username']
        game_title = data['gameTitle']
        quantity = data['numCopies']
        added = add_reservation(username, game_title, quantity)

        if not added:
            raise Exception("Errore nel recupero di copie rimanenti")

        return jsonify({'error': False, 'message': 'Reservation added successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid add reservation format'}), 400
    except BadRequest as e:
        return jsonify({'error': True, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Add reservation failed: {str(e)}'}), 500

@app.route('/deleteReservation/<string:reservation_id>', methods=['DELETE'])
def delete_reservation_route(reservation_id):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401
        deleted = delete_reservation(reservation_id)
        if deleted:
            return jsonify({'error': False, 'message': 'User fetched successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get reservation format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get reservation failed: {str(e)}'}), 500

@app.route('/addPurchase', methods=['POST'])
def add_purchase_route():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        data = request.get_json()

        username = data['username']
        game_title = data['gameTitle']
        quantity = data['numCopies']
        response = add_purchase(username, game_title, quantity)

        if not response:
            raise Exception("Errore nel recupero di copie rimanenti")


        notify_game_catalog_game(game_title, response["remaining_copies"])

        #notify_game_catalog_game(game_title, remaining_copies) #TODO: Implementare notifica ad utente admin

        return jsonify({'response': response,'error': False, 'message': 'Reservation added successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid add reservation format'}), 400
    except BadRequest as e:
        return jsonify({'error': True, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Add reservation failed: {str(e)}'}), 500

@app.route('/getPurchases/<string:username>', methods=['GET'])
def get_purchases_route(username):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401
        purchases = get_purchases(username)
        return jsonify({'purchases': purchases, 'error': False, 'message': 'User fetched successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get reservation format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get reservation failed: {str(e)}'}), 500

@app.route('/getAllPurchases', methods=['GET'])
def get_all_purchases_route():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401
        purchases = get_all_purchases()
        logger.info(f"\n\n\nAll purchases {purchases}\n\n\n")
        return jsonify({'purchases': purchases, 'error': False, 'message': 'User fetched successfully'}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get reservation format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Get reservation failed: {str(e)}'}), 500

if __name__ == '__main__':
    kafka_thread_2 = threading.Thread(target=listen_game_catalog, daemon=True)
    kafka_thread_2.start()
    app.run(host='0.0.0.0', port=3002, threaded=True)
