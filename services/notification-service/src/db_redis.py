import redis
import json
from datetime import datetime
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

NOTIFICATIONS_KEY = os.getenv("NOTIFICATIONS_KEY", "notifications")
READ_STATUS_KEY_PREFIX = os.getenv("READ_STATUS_KEY_PREFIX", "notification_reads:")


# Funzione per aggiungere una nuova notifica
def add_notification(message, users):
    notification_id = r.incr("notification_id_counter")
    timestamp = datetime.now().isoformat()

    # Salva la notifica in Redis
    notification = {
        "id": notification_id,
        "message": message,
        "timestamp": timestamp
    }
    r.hset(NOTIFICATIONS_KEY, notification_id, json.dumps(notification))

    # Salva lo stato di lettura per ciascun utente
    for user in users:
        r.hset(f"{READ_STATUS_KEY_PREFIX}{user}", notification_id, 0)  # 0 = non letto

    return notification_id


# Funzione per aggiungere una notifica solo per l'amministratore
def add_notification_to_admin(message):
    admin_user = "admin"
    notification_id = add_notification(message, [admin_user])
    if notification_id:
        return notification_id
    else:
        raise ValueError(f"Errore creazione notifica per l'admin")


# Funzione per ottenere tutte le notifiche non lette per un utente
def get_unread_notifications(username):
    user_read_status_key = f"{READ_STATUS_KEY_PREFIX}{username}"
    unread_notifications = []

    # Controlla tutte le notifiche
    for notification_id, status in r.hgetall(user_read_status_key).items():
        if status == "0":  # 0 = non letto
            notification_data = r.hget(NOTIFICATIONS_KEY, notification_id)
            if notification_data:
                unread_notifications.append(json.loads(notification_data))

    return unread_notifications


# Funzione per segnare una notifica come letta per un utente specifico
def mark_notification_as_read(username, notification_id):
    user_read_status_key = f"{READ_STATUS_KEY_PREFIX}{username}"
    if r.hexists(user_read_status_key, notification_id):
        r.hset(user_read_status_key, notification_id, 1)  # 1 = letto
        return True
    else:
        raise ValueError(f"Notifica ID {notification_id} non trovata per l'utente {username}.")


# Funzione per ottenere tutte le notifiche di un utente (lette e non lette)
def get_all_notifications(username):
    user_read_status_key = f"{READ_STATUS_KEY_PREFIX}{username}"
    all_notifications = []

    for notification_id in r.hkeys(user_read_status_key):
        notification_data = r.hget(NOTIFICATIONS_KEY, notification_id)
        if notification_data:
            all_notifications.append(json.loads(notification_data))

    return all_notifications


# Funzione per cancellare tutte le notifiche
def clear_database():
    r.delete(NOTIFICATIONS_KEY)
    for key in r.keys(f"{READ_STATUS_KEY_PREFIX}*"):
        r.delete(key)

"""
# Test delle funzioni
if __name__ == "__main__":
    # Simulazione utenti
    users = ["user1", "user2", "admin"]

    # Pulisce il database
    clear_database()

    # Aggiungi una notifica
    notification_id = add_notification("Benvenuto nel sistema di notifiche!", users)
    print(f"Notifica aggiunta con ID {notification_id}")

    # Aggiungi una notifica per l'amministratore
    admin_notification_id = add_notification_to_admin("Messaggio importante per l'admin!", users)
    print(f"Notifica aggiunta per l'admin con ID {admin_notification_id}")

    # Ottieni notifiche non lette per user1
    unread_notifications = get_unread_notifications("user1")
    print(f"Notifiche non lette per user1: {unread_notifications}")

    # Segna una notifica come letta
    mark_notification_as_read("user1", notification_id)
    print(f"Notifica {notification_id} segnata come letta per user1")

    # Ottieni tutte le notifiche di user1
    all_notifications = get_all_notifications("user1")
    print(f"Tutte le notifiche per user1: {all_notifications}")
"""