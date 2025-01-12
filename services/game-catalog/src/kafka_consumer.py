from kafka import KafkaConsumer
import json
from mongo_db import MongoDB
import threading
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

consumer = KafkaConsumer(
    'user-registrations',
    'game-modify',
    group_id='game-catalog',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    fetch_max_bytes=209715200
)

class KafkaConsumerError(Exception):
    """Eccezione personalizzata per errori del consumatore Kafka."""
    pass

class InvalidMessageError(Exception):
    """Eccezione per messaggi non validi."""
    pass

def listen_order_service():
    db = MongoDB.get_instance()
    while True:
        try:
            for message in consumer:
                try:
                    # Verifica del messaggio ricevuto
                    if not message or not message.value:
                        raise InvalidMessageError("Messaggio vuoto ricevuto.")

                    # Filtraggio del topic
                    if message.topic == 'user-registrations':
                        handle_user_registration(message, db)
                    elif message.topic == 'game-modify':
                        handle_game_modify(message, db)
                    else:
                        print(f"Messaggio da un topic sconosciuto: {message.topic}")
                        continue

                except InvalidMessageError as ime:
                    # Gestione degli errori relativi a messaggi non validi
                    print(f"Errore messaggio non valido: {str(ime)}")
                    raise ime
                except Exception as e:
                    # Gestione generale degli errori per il messaggio
                    raise KafkaConsumerError(f"Errore durante l'elaborazione del messaggio: {message}. Dettagli: {str(e)}") from e

        except KafkaConsumerError as kce:
            # Gestione degli errori generali del consumatore Kafka
            print(f"Errore Kafka Consumer: {str(kce)}. Tentativo di ripresa...")
            import time
            time.sleep(5)
        except Exception as e:
            # Gestione di eventuali altre eccezioni
            print(f"Errore imprevisto nel ciclo Kafka Consumer: {str(e)}")
            raise

def handle_user_registration(message, db):
    # Estrazione del contenuto
    username = message.value.get('username')
    if not username:
        raise InvalidMessageError("Messaggio senza username.")

    # Verifica se l'utente esiste nel database
    if db.user_collection.find_one({"username": username}):
        raise KafkaConsumerError(f"L'utente {username} esiste già nel database.")
    else:
        # Inserimento nel database
        db.user_collection.insert_one({"username": username, "reviews": []})
        print(f"Utente {username} registrato con successo nel database.")

def handle_game_modify(message, db):
    game_title = message.value.get('game_title')
    if not game_title:
        raise InvalidMessageError("Messaggio senza game_title.")

    remaining_copies = message.value.get('remaining_copies')
    if not remaining_copies:
        raise InvalidMessageError("Messaggio senza remaining_copies.")

    game = db.game_collection.find_one({"title": game_title})
    if not game:
        raise KafkaConsumerError(f"Il gioco '{game_title}' non esiste nel database.")

    result = db.game_collection.update_one(
        {"title": game_title},  # Filtro
        {"$set": {"stock": remaining_copies}}
    )

    if result.matched_count == 0:
        raise KafkaConsumerError(
            f"Errore nell'aggiornamento di '{game_title}': nessun documento corrispondente trovato.")

    print(f"Il gioco '{game_title}' è stato aggiornato con {remaining_copies} copie rimanenti.")
