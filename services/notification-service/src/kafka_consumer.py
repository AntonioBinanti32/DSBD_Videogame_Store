from kafka import KafkaConsumer
import json
import threading
import logging
from db_redis import *
from redis import StrictRedis
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

KAFKA_URI = os.getenv("KAFKA_URI")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

redis_client = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


consumer = KafkaConsumer(
    "notification",
    "admin-notification",
    bootstrap_servers=[KAFKA_URI],
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    fetch_max_bytes=209715200
)

class KafkaConsumerError(Exception):
    """Eccezione personalizzata per errori del consumatore Kafka."""
    pass

class InvalidMessageError(Exception):
    """Eccezione per messaggi non validi."""
    pass

def listen_services():
    while True:
        try:
            for message in consumer:
                try:
                    # Verifica del messaggio ricevuto
                    if not message or not message.value:
                        raise InvalidMessageError("Messaggio vuoto ricevuto.")

                    # Filtraggio del topic
                    if message.topic == 'notification':
                        handle_notifications(message)
                    elif message.topic == 'admin-notification':
                        handle_admin_notifications(message)
                    else:
                        logger.info(f"Messaggio da un topic sconosciuto: {message.topic}")
                        continue

                except InvalidMessageError as ime:
                    # Gestione degli errori relativi a messaggi non validi
                    logger.info(f"Errore messaggio non valido: {str(ime)}")
                    raise ime
                except Exception as e:
                    # Gestione generale degli errori per il messaggio
                    raise KafkaConsumerError(f"Errore durante l'elaborazione del messaggio: {message}. Dettagli: {str(e)}") from e

        except KafkaConsumerError as kce:
            # Gestione degli errori generali del consumatore Kafka
            logger.info(f"Errore Kafka Consumer: {str(kce)}. Tentativo di ripresa...")
            import time
            time.sleep(5)
        except Exception as e:
            # Gestione di eventuali altre eccezioni
            logger.info(f"Errore imprevisto nel ciclo Kafka Consumer: {str(e)}")
            raise

def handle_notifications(message):
    notification = message.value
    message_body = notification["message"]
    if not message_body:
        raise InvalidMessageError("Messaggio senza message body.")
    users = notification["users"]
    if not users:
        raise InvalidMessageError("Messaggio senza lista utenti.")
    notification_id = add_notification(message_body, users)

    return notification_id

def handle_admin_notifications(message):
    notification = message.value
    message_body = notification["message"]
    if not message_body:
        raise InvalidMessageError("Messaggio senza message body.")
    notification_id = add_notification_to_admin(message_body)

    return notification_id