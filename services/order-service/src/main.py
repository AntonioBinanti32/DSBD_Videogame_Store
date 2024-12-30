#TODO: Completare
from flask import Flask, jsonify
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine("postgresql://postgres:password@postgres:5432/orders")

@app.route("/")
def home():
    return jsonify({"message": "Order Service is running!"})

@app.route("/orders", methods=["GET"])
def get_orders():
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM orders")
        orders = [dict(row) for row in result]
    return jsonify(orders)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

