from kafka import KafkaConsumer
import json
from mongo_db import MongoDB
import threading

consumer = KafkaConsumer(
    'user-registrations',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

class KafkaConsumerError(Exception):
    """Eccezione personalizzata per errori del consumatore Kafka."""
    pass

class InvalidMessageError(Exception):
    """Eccezione per messaggi non validi."""
    pass

def listen_for_user_registrations():
    db = MongoDB.get_instance()
    while True:
        try:
            for message in consumer:
                try:
                    # Verifica del messaggio ricevuto
                    if not message or not message.value:
                        raise InvalidMessageError("Messaggio vuoto ricevuto.")

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
