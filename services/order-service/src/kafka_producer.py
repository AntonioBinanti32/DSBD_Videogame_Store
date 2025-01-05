from kafka import KafkaProducer
from kafka.errors import KafkaError
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class NotificationError(Exception):
    """Eccezione personalizzata per errori di notifica verso Kafka."""
    pass


def notify_game_catalog(username):
    try:
        # Controllo che lo username sia una stringa valida
        if not username or not isinstance(username, str):
            raise ValueError("Lo username deve essere una stringa non vuota.")

        # Creazione del messaggio
        message = {"username": username}

        # Invio del messaggio al topic Kafka
        future = producer.send('user-registrations', value=message)

        # Controllo se l'invio ha avuto successo
        result = future.get(timeout=10)  # Timeout per prevenire attese infinite
        print(f"Messaggio inviato con successo a Kafka: {result}")

    except KafkaError as ke:
        # Gestione degli errori di Kafka
        raise NotificationError(f"Errore durante l'invio del messaggio a Kafka: {str(ke)}") from ke

    except ValueError as ve:
        # Gestione degli errori relativi al messaggio
        raise NotificationError(f"Errore nella validazione del messaggio: {str(ve)}") from ve

    except Exception as e:
        # Gestione di errori generici
        raise NotificationError(f"Errore imprevisto durante la notifica a Kafka: {str(e)}") from e
