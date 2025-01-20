from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
import os
import time
from metrics import MESSAGES_PROCESSED, REQUEST_LATENCY

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

KAFKA_URI = os.getenv("KAFKA_URI")

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URI],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    max_request_size=209715200
)

class NotificationError(Exception):
    """Eccezione personalizzata per errori di notifica verso Kafka."""
    pass


def notify_game_catalog_signup(username):
    try:
        start_time = time.time()
        if not username or not isinstance(username, str):
            raise ValueError("Lo username deve essere una stringa non vuota.")

        message = {"username": username}
        logger.info(f"\n\n\nMessaggio da inviare: {message}\n\n\n")
        future = producer.send('user-registrations', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_order_service").observe(time.time() - start_time)

def notify_game_catalog_game(game_title, remaining_copies):
    try:
        start_time = time.time()
        if not game_title or not isinstance(game_title, str):
            raise ValueError("game_title deve essere una stringa non vuota.")
        if not remaining_copies or not isinstance(remaining_copies, int):
            raise ValueError("remaining_copies deve essere una stringa non vuota.")

        message = {
            "game_title": game_title,
            "remaining_copies": remaining_copies}

        future = producer.send('game-modify', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_order_service").observe(time.time() - start_time)

def notify_notification_service(users_list, message):
    try:
        start_time = time.time()
        if not users_list or not isinstance(users_list, list):
            raise ValueError("user_list deve essere una lista non vuota.")
        if not message or not isinstance(message, str):
            raise ValueError("message deve essere una stringa non vuota.")

        message = {
            "users": users_list,
            "message": message}

        future = producer.send('notification', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_order_service").observe(time.time() - start_time)

def notify_notification_service_admin(message):
    try:
        start_time = time.time()
        if not message or not isinstance(message, str):
            raise ValueError("message deve essere una stringa non vuota.")

        message = {"message": message}

        future = producer.send('admin-notification', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_order_service").observe(time.time() - start_time)