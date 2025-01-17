from kafka import KafkaConsumer
import json
import threading
import logging
from db_postgres import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

KAFKA_URI = os.getenv("KAFKA_URI")

consumer = KafkaConsumer(
    'order-service-add-game',
    'order-service-update-game',
    'order-service-delete-game',
    group_id='order-service',
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

def listen_game_catalog():
    while True:
        try:
            for message in consumer:
                try:
                    # Verifica del messaggio ricevuto
                    if not message or not message.value:
                        raise InvalidMessageError("Messaggio vuoto ricevuto.")

                    # Filtraggio del topic
                    if message.topic == 'order-service-add-game':
                        handle_add_game(message)
                    elif message.topic == 'order-service-update-game':
                        handle_update_game(message)
                    elif message.topic == 'order-service-delete-game':
                        handle_delete_game(message)
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

def handle_add_game(message):
    title = message.value.get('title')
    if not title:
        raise InvalidMessageError("Messaggio senza title.")

    stock = message.value.get('stock')
    if not stock:
        raise InvalidMessageError("Messaggio senza stock.")

    price = message.value.get('price')
    if not price:
        raise InvalidMessageError("Messaggio senza price.")

    result = add_game(title, stock, price)

    if not result:
        raise KafkaConsumerError(
            f"Errore nella creazione di '{title}' nel db postgres")

def handle_update_game(message):
    title = message.value.get('title')
    if not title:
        raise InvalidMessageError("Messaggio senza title.")

    stock = message.value.get('stock')
    if not stock:
        raise InvalidMessageError("Messaggio senza stock.")

    price = message.value.get('price')
    if not price:
        raise InvalidMessageError("Messaggio senza price.")

    result = update_game(title, None, stock, price)

    if not result:
        raise KafkaConsumerError(
            f"Errore nella modifica di '{title}' nel db postgres")

def handle_delete_game(message):
    title = message.value.get('title')
    if not title:
        raise InvalidMessageError("Messaggio senza title.")
    result = delete_game(title)

    if not result:
        raise KafkaConsumerError(
            f"Errore nella modifica di '{title}' nel db postgres")