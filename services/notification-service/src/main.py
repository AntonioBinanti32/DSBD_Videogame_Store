#TODO: Completare
from flask import Flask, jsonify
import redis

app = Flask(__name__)
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

@app.route("/")
def home():
    return jsonify({"message": "Notification Service is running!"})

@app.route("/notifications", methods=["GET"])
def get_notifications():
    notifications = redis_client.lrange("notifications", 0, -1)
    return jsonify(notifications)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
