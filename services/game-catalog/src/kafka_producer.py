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
    bootstrap_servers=['my-kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    max_request_size=209715200
)

class NotificationError(Exception):
    """Eccezione personalizzata per errori di notifica verso Kafka."""
    pass


def notify_order_service_add_game(title, stock, price):
    try:
        start_time = time.time()
        if not title or not isinstance(title, str):
            raise ValueError("Il titolo deve essere una stringa non vuota.")

        if not stock or not isinstance(stock, int):
            raise ValueError("Il numero di copie deve essere una stringa non vuota.")

        if not price or not isinstance(price, float):
            raise ValueError("Il prezzo deve essere una stringa non vuota.")

        message = {"title": title, "stock": stock, "price": price}

        future = producer.send('order-service-add-game', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")
    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_game_catalog").observe(time.time() - start_time)

def notify_order_service_update_game(title, stock, price):
    try:
        start_time = time.time()
        if not title or not isinstance(title, str):
            raise ValueError("Il titolo deve essere una stringa non vuota.")

        message = {"title": title, "stock": stock, "price": price}

        future = producer.send('order-service-update-game', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_game_catalog").observe(time.time() - start_time)

def notify_order_service_delete_game(title):
    try:
        start_time = time.time()
        if not title or not isinstance(title, str):
            raise ValueError("Il titolo deve essere una stringa non vuota.")

        message = {"title": title}

        future = producer.send('order-service-delete-game', value=message)

        result = future.get(timeout=10)
        logger.info(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
    finally:
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_game_catalog").observe(time.time() - start_time)

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
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_game_catalog").observe(time.time() - start_time)

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
        REQUEST_LATENCY.labels(endpoint="kafka_message_producer_game_catalog").observe(time.time() - start_time)