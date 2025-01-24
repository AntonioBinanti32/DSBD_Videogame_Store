import redis
import json
from datetime import datetime
import os
from metrics import DB_REQUEST_COUNT, DB_REQUEST_LATENCY
import time

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

NOTIFICATIONS_KEY = os.getenv("NOTIFICATIONS_KEY", "notifications")
READ_STATUS_KEY_PREFIX = os.getenv("READ_STATUS_KEY_PREFIX", "notification_reads:")

# Funzione per aggiungere una nuova notifica
def add_notification(message, users):
    notification_id = r.incr("notification_id_counter")
    timestamp = datetime.now().isoformat()

    start_time = time.time()

    # Salva la notifica in Redis
    notification = {
        "id": notification_id,
        "message": message,
        "timestamp": timestamp
    }

    # Salva lo stato di lettura per ciascun utente
    for user in users:
        r.hset(f"{READ_STATUS_KEY_PREFIX}{user}", notification_id, 0)  # 0 = non letto

    r.hset(NOTIFICATIONS_KEY, notification_id, json.dumps(notification))
    DB_REQUEST_LATENCY.labels(endpoint="redis_add_notification").observe(time.time() - start_time)
    DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_add_notification", http_status=200).inc()
    return notification_id


# Funzione per aggiungere una notifica solo per l'amministratore
def add_notification_to_admin(message):
    admin_user = "admin"
    start_time = time.time()
    notification_id = add_notification(message, [admin_user])
    if notification_id:
        DB_REQUEST_LATENCY.labels(endpoint="redis_add_notification_to_admin").observe(time.time() - start_time)
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_add_notification_to_admin", http_status=200).inc()
        return notification_id
    else:
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_add_notification_to_admin", http_status=500).inc()
        raise ValueError(f"Errore creazione notifica per l'admin")


# Funzione per ottenere tutte le notifiche non lette per un utente
def get_unread_notifications(username):
    user_read_status_key = f"{READ_STATUS_KEY_PREFIX}{username}"
    unread_notifications = []
    start_time = time.time()
    # Controlla tutte le notifiche
    for notification_id, status in r.hgetall(user_read_status_key).items():
        if status == "0":  # 0 = non letto
            notification_data = r.hget(NOTIFICATIONS_KEY, notification_id)
            if notification_data:
                unread_notifications.append(json.loads(notification_data))

    DB_REQUEST_LATENCY.labels(endpoint="redis_get_unread_notification").observe(time.time() - start_time)
    DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_get_unread_notification", http_status=200).inc()
    return unread_notifications


# Funzione per segnare una notifica come letta per un utente specifico
def mark_notification_as_read(username, notification_id):
    user_read_status_key = f"{READ_STATUS_KEY_PREFIX}{username}"
    start_time = time.time()
    if r.hexists(user_read_status_key, notification_id):
        r.hset(user_read_status_key, notification_id, 1)  # 1 = letto
        DB_REQUEST_LATENCY.labels(endpoint="redis_mark_notification_as_read").observe(time.time() - start_time)
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_mark_notification_as_read", http_status=200).inc()
        return True
    else:
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_mark_notification_as_read", http_status=500).inc()
        raise ValueError(f"Notifica ID {notification_id} non trovata per l'utente {username}.")


# Funzione per ottenere tutte le notifiche di un utente (lette e non lette)
def get_all_notifications(username):
    user_read_status_key = f"{READ_STATUS_KEY_PREFIX}{username}"
    all_notifications = []
    start_time = time.time()
    for notification_id in r.hkeys(user_read_status_key):
        notification_data = r.hget(NOTIFICATIONS_KEY, notification_id)
        if notification_data:
            all_notifications.append(json.loads(notification_data))

    DB_REQUEST_LATENCY.labels(endpoint="redis_get_all_notifications").observe(time.time() - start_time)
    DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_get_all_notifications", http_status=200).inc()
    return all_notifications


# Funzione per cancellare tutte le notifiche
def clear_database():
    start_time = time.time()
    r.delete(NOTIFICATIONS_KEY)
    for key in r.keys(f"{READ_STATUS_KEY_PREFIX}*"):
        r.delete(key)
    DB_REQUEST_LATENCY.labels(endpoint="redis_clear_database").observe(time.time() - start_time)
    DB_REQUEST_COUNT.labels(method="function_call", endpoint="redis_clear_database", http_status=200).inc()