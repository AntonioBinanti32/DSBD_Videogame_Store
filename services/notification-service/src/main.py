from kafka_consumer import *
from flask import Flask, request, jsonify
import jwt
import datetime
from werkzeug.exceptions import BadRequest
import os
import threading
from db_redis import *

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

app = Flask(__name__)
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


# Funzione per verificare il token JWT
def verify_token(token, username, secret_key):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        if decoded_token.get('username') == username:
            return True
        else:
            raise BadRequest('Invalid username in token')
    except jwt.ExpiredSignatureError:
        raise BadRequest('Token expired')
    except jwt.InvalidTokenError:
        raise BadRequest('Invalid token')

@app.route("/")
def home():
    return jsonify({"message": "Notification Service is running!"})

@app.route("/getAllNotifications/<string:username>", methods=["GET"])
def get_all_notifications_route(username):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401
        notifications = get_all_notifications(username)
        return jsonify({'notifications': notifications, 'error': False}), 200

    except KeyError:
        return jsonify({'error': True, 'message': 'Invalid get all notification format'}), 400
    except Exception as e:
        return jsonify({'error': True, 'message': f'Error fetching notifications: {str(e)}'}), 500

@app.route("/getUnreadNotifications/<string:username>", methods=["GET"])
def unread_notification_route(username):
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        unread_notifications = get_unread_notifications(username)
        return jsonify({'unread_notifications': unread_notifications, 'error': False}), 200

    except Exception as e:
        return jsonify({'error': True, 'message': f'Error fetching unread notifications: {str(e)}'}), 500
@app.route("/markNotificationAsRead", methods=["POST"])
def mark_notification_route():
    try:
        actual_user = request.headers.get('Actualuser')
        token = request.headers.get('Token')

        if not verify_token(token, actual_user, JWT_SECRET_KEY):
            return jsonify({'error': True, 'message': 'Token verification failed'}), 401

        data = request.json
        username = data.get('Username')
        notification_id = data.get('NotificationID')
        success = mark_notification_as_read(username, notification_id)
        if success:
            return jsonify({"error": False, "message": "Notification marked as read"}), 200
        else:
            return jsonify({"error": True, "message": "Notification not found for the user"}), 404

    except KeyError:
        return jsonify({"error": True, "message": "Invalid request format"}), 400
    except Exception as e:
        return jsonify({"error": True, "message": f"Failed to mark notification as read: {str(e)}"}), 500


if __name__ == "__main__":
    kafka_thread_3 = threading.Thread(target=listen_services, daemon=True)
    kafka_thread_3.start()
    app.run(host="0.0.0.0", port=3003, threaded=True)
