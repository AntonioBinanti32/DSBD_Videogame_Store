#TODO: Da completare
from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb://mongo:27017/")
db = client["game-catalog"]

@app.route("/")
def home():
    return jsonify({"message": "Game Catalog Service is running!"})

@app.route("/games", methods=["GET"])
def get_games():
    games = list(db.games.find({}, {"_id": 0}))
    return jsonify(games)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
