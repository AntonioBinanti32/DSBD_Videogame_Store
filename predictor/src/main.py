from flask import Flask, jsonify, request
import requests
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import os
from prometheus_client import Gauge, generate_latest, REGISTRY
import logging
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090/api/v1/query")
PREDICTOR_COUNTER_LIMIT = int(os.getenv("PREDICTOR_COUNTER_LIMIT", "2"))
PREDICTOR_COUNTER = 0

CPU_PREDICTION = Gauge(
    'predicted_cpu_usage',
    'Predicted CPU usage for the next time steps',
    ['timestamp', 'job']#,
    #registry=REGISTRY
)

HTTP_REQUEST_PREDICTION = Gauge(
    'predicted_http_requests',
    'Predicted HTTP requests for the next time steps',
    ['timestamp', 'job']#,
    #registry=REGISTRY
)

@app.route('/metrics', methods=['GET'])
def metrics():
    global PREDICTOR_COUNTER
    PREDICTOR_COUNTER += 1
    if PREDICTOR_COUNTER > PREDICTOR_COUNTER_LIMIT:
        predict()
        PREDICTOR_COUNTER = 0
    return generate_latest(REGISTRY), 200, {'Content-Type': 'text/plain'}


@app.route('/predict', methods=['GET'])
def predict():
    metrics = {}

    # Fetch delle metriche Prometheus
    metrics['http_requests'] = fetch_metric('http_requests_total[5m]')
    metrics['cpu_usage'] = fetch_metric('container_cpu_usage_seconds_total[5m]')

    if not metrics['http_requests'] or not metrics['cpu_usage']:
        return jsonify({"error": "Insufficient data for prediction"}), 404

    predictions = {}

    for job, df in metrics['http_requests'].items():
        if df.empty:
            continue
        predictions[f'http_requests_{job}'] = apply_arima(df)

    for job, df in metrics['cpu_usage'].items():
        if df.empty:
            continue
        predictions[f'cpu_usage_{job}'] = apply_arima(df)

        for value in predictions[f'cpu_usage_{job}']:
            CPU_PREDICTION.labels(job=job, timestamp=value["timestamp"]).set(value["value"])

    for job, prediction in predictions.items():
        if 'http_requests' in job:
            for value in prediction:
                HTTP_REQUEST_PREDICTION.labels(job=job, timestamp=value["timestamp"]).set(value["value"])

    return jsonify(predictions)

def fetch_metric(query):
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query})

        if response.status_code != 200:
            logger.error(f"Errore durante il fetch della metrica {query}: {response.status_code}")
            return None

        datas = response.json().get('data', {}).get('result', [])
        if not datas:
            logger.warning(f"Nessun risultato per la query: {query}")
            return None

        result = {}
        for data in datas:
            metric = data.get("metric", {})
            job = metric.get("job", "unknown")
            values = data.get('values', [])

            if not values:
                logger.warning(f"Nessun valore trovato per il job: {job}")
                continue

            # Conversione in DataFrame
            df = pd.DataFrame(values, columns=['timestamp', 'value'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df['value'] = df['value'].astype(float)
            df.set_index('timestamp', inplace=True)

            result[job] = df
        logger.info(f"\n\n\nResults:\n{result}\n\n\n")
        return result
    except Exception as e:
        logger.error(f"Errore durante il fetch della metrica {query}: {e}")
        return None

def apply_arima(df):
    try:
        model = ARIMA(df['value'], order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=10)

        future_timestamps = pd.date_range(df.index[-1], periods=11, freq='15s')[
                            1:]
        forecast_with_timestamps = pd.Series(forecast.values, index=future_timestamps)
        logger.info(forecast_with_timestamps)

        forecast_list = [{"timestamp": timestamp.isoformat(), "value": value} for timestamp, value in
                         forecast_with_timestamps.items()]

        return forecast_list

    except Exception as e:
        logger.error(f"Errore durante l'applicazione del modello ARIMA: {e}")
        return []

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
