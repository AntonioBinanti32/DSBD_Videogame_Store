from prometheus_client import Counter, Histogram, CollectorRegistry

# Registry personalizzata
PROMETHEUS_REGISTRY = CollectorRegistry()

# Definizione delle metriche con la nuova registry
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status'],
    registry=PROMETHEUS_REGISTRY
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latency of HTTP requests in seconds',
    ['endpoint'],
    registry=PROMETHEUS_REGISTRY
)

DB_REQUEST_COUNT = Counter(
    'db_requests_total',
    'Total databases requests',
    ['method', 'endpoint', 'http_status'],
    registry=PROMETHEUS_REGISTRY
)

DB_REQUEST_LATENCY = Histogram(
    'db_request_duration_seconds',
    'Latency of databases requests in seconds',
    ['endpoint'],
    registry=PROMETHEUS_REGISTRY
)

MESSAGES_PROCESSED = Counter('kafka_messages_processed_total', 'Total number of messages processed from Kafka', ['topic'], registry=PROMETHEUS_REGISTRY)
