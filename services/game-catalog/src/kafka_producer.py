from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    max_request_size=209715200
)

class NotificationError(Exception):
    """Eccezione personalizzata per errori di notifica verso Kafka."""
    pass


def notify_order_service_add_game(title, stock, price):
    try:
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

def notify_order_service_update_game(title, stock, price):
    try:
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

def notify_order_service_delete_game(title):
    try:
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