import jwt
import datetime
import psycopg2
import bcrypt
from werkzeug.exceptions import BadRequest
import os
import logging
from decimal import Decimal
from metrics import DB_REQUEST_COUNT, DB_REQUEST_LATENCY
import time

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

# Connessione a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    return conn

# Funzione per generare il token JWT
def generate_jwt_token(username, secret_key):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Il token scade dopo 1 giorno
    token = jwt.encode({'username': username, 'exp': expiration_time}, secret_key, algorithm='HS256')
    return token

# Funzione per verificare il token JWT
def verify_token(token, username, secret_key):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        if decoded_token.get('username') == username:
            return True
        else:
            raise BadRequest('Invalid username in token')
    except jwt.ExpiredSignatureError:
        raise BadRequest('Token expired')
    except jwt.InvalidTokenError:
        raise BadRequest('Invalid token')

# Funzione per registrare un utente
def signup(username, password, image_url):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM all_users WHERE username = %s', (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise BadRequest('Utente già registrato')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cursor.execute('''
                INSERT INTO all_users (username, password, image_url)
                VALUES (%s, %s, %s)
            ''', (username, hashed_password, image_url or "https://www.iconpacks.net/icons/2/free-user-icon-3297-thumb.png"))
        logger.info(f"\n\n\nAsh pwd: {hashed_password}\n\n\n")
        conn.commit()
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_signup", http_status=200).inc()
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_signup", http_status=500).inc()
        raise BadRequest(f'Error while adding signup: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_signup").observe(time.time() - start_time)


# Funzione per effettuare il login
def login(username, password):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM all_users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            conn.close()
            raise BadRequest('Username o password errati')
        stored_password = user[2]

        if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            cursor.close()
            conn.close()
            raise BadRequest('Username o password errati')

        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_login", http_status=200).inc()
        return user
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_login", http_status=500).inc()
        raise BadRequest(f'Error while logging user: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_login").observe(time.time() - start_time)

def get_user(username):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT username, image_url FROM all_users WHERE username = %s', (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            raise BadRequest('User not found')
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_user", http_status=200).inc()
        return {'username': user[0], 'image_url': user[1]}
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_user", http_status=500).inc()
        raise BadRequest(f'Error while getting user: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_get_user").observe(time.time() - start_time)

def add_game(title, stock, price):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM games WHERE title = %s', (title,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            raise BadRequest('Gioco già esistente')

        cursor.execute('''
                    INSERT INTO games (title, num_copies, price)
                    VALUES (%s, %s, %s)
                ''', (
        title, stock, price))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_add_game", http_status=500).inc()
        raise BadRequest(f'Error while adding game: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_add_game", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_add_game").observe(time.time() - start_time)
        return True


def update_game(title, new_title=None, stock=None, price=None):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM games WHERE title = %s', (title,))
        game = cursor.fetchone()
        if not game:
            cursor.close()
            conn.close()
            raise BadRequest('Gioco non trovato')

        update_values = []
        update_columns = []

        if new_title is not None:
            update_columns.append('title = %s')
            update_values.append(new_title)
        if stock is not None:
            if not isinstance(stock, int):
                raise BadRequest("La quantità di copie deve essere un numero intero")
            update_columns.append('num_copies = %s')
            update_values.append(stock)
        if price is not None:
            if not isinstance(price, (float, int)):
                raise BadRequest("Il prezzo deve essere un numero decimale")
            update_columns.append('price = %s')
            update_values.append(price)

        update_values.append(title)

        update_query = f'''
            UPDATE games
            SET {", ".join(update_columns)}
            WHERE title = %s
        '''

        cursor.execute(update_query, tuple(update_values))
        conn.commit()

    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_update_game", http_status=500).inc()
        raise BadRequest(f'Errore durante l\'aggiornamento del gioco: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_update_game", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_update_game").observe(time.time() - start_time)
        return True



def delete_game(title):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM games WHERE title = %s', (title,))
        game = cursor.fetchone()
        if not game:
            cursor.close()
            conn.close()
            raise BadRequest('Gioco non trovato')

        cursor.execute('DELETE FROM games WHERE title = %s', (title,))
        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_delete_game", http_status=500).inc()
        raise BadRequest(f'Errore durante l\'eliminazione del gioco: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_delete_game", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_delete_game").observe(time.time() - start_time)


def get_reservations(username):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""SELECT
                r.id as _id, 
                u.username,
                g.title AS game_title,
                r.num_copies,
                r.price,
                r.reservation_date
            FROM 
                reservations r
            JOIN 
                all_users u ON r.user_id = u.id
            JOIN 
                games g ON r.game_id = g.id
            WHERE 
                u.username = %s""", (username,))
        reservations = cursor.fetchall()
        reservation_list = [
            {
                '_id': row[0],
                'username': row[1],
                'game_title': row[2],
                'num_copies': int(row[3]),
                'price': float(row[4]) if isinstance(row[4], Decimal) else row[4],
                'reservation_date': row[5]
            }
            for row in reservations
        ]

        return reservation_list
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_reservations", http_status=500).inc()
        raise BadRequest(f'Error while getting reservation: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_reservations", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_get_reservations").observe(time.time() - start_time)

def add_reservation(username, game_title, num_copies):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM all_users WHERE username = %s', (username,))
        user = cursor.fetchone()
        if not user:
            raise BadRequest('User not found')
        user_id = user[0]

        cursor.execute('SELECT id, num_copies, price FROM games WHERE title = %s', (game_title,))
        game = cursor.fetchone()
        if not game:
            raise BadRequest('Game not found')
        game_id, available_copies, price = game

        if num_copies > available_copies:
            raise BadRequest('Not enough copies available')

        cursor.execute('''
            SELECT 1 FROM reservations
            WHERE user_id = %s AND game_id = %s
        ''', (user_id, game_id))
        if cursor.fetchone():
            raise BadRequest('The game has already been reserved by this user')

        reservation_date = datetime.datetime.utcnow()
        cursor.execute('''
            INSERT INTO reservations (user_id, game_id, num_copies, price, reservation_date)
            VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, game_id, num_copies, price, reservation_date))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_add_reservation", http_status=500).inc()
        raise BadRequest(f'Error while adding reservation: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_add_reservation", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_add_reservation").observe(time.time() - start_time)

def delete_reservation(reservation_id):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Recupera i dettagli della prenotazione per aggiornare le copie disponibili
        cursor.execute('''
            SELECT game_id, num_copies 
            FROM reservations 
            WHERE id = %s
        ''', (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            raise BadRequest('Reservation not found')

        game_id, num_copies = reservation

        # Elimina la prenotazione
        cursor.execute('DELETE FROM reservations WHERE id = %s', (reservation_id,))

        # Ripristina il numero di copie nel gioco associato
        cursor.execute('''
            UPDATE games
            SET num_copies = num_copies + %s
            WHERE id = %s
        ''', (num_copies, game_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_delete_reservation", http_status=500).inc()
        raise BadRequest(f'Error while deleting reservation: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_delete_reservation", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_delete_reservation").observe(time.time() - start_time)

def add_purchase(username, game_title, num_copies):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verifica se l'utente esiste
        cursor.execute('SELECT id FROM all_users WHERE username = %s', (username,))
        user = cursor.fetchone()
        if not user:
            raise BadRequest('User not found')
        user_id = user[0]

        # Verifica se il gioco esiste e ottieni il numero di copie e il prezzo
        cursor.execute('SELECT id, num_copies, price FROM games WHERE title = %s', (game_title,))
        game = cursor.fetchone()
        if not game:
            raise BadRequest('Game not found')
        game_id, available_copies, price = game

        # Controlla se ci sono abbastanza copie disponibili
        if num_copies > available_copies:
            raise BadRequest('Not enough copies available')

        # Calcola il prezzo totale
        total_price = price * num_copies

        # Inserisce l'acquisto nella tabella purchases
        purchase_date = datetime.datetime.utcnow()
        cursor.execute('''
            INSERT INTO purchases (user_id, game_id, num_copies, total_price, purchase_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', (user_id, game_id, num_copies, total_price, purchase_date))
        purchase_id = cursor.fetchone()[0]

        # Aggiorna il numero di copie disponibili nel gioco
        cursor.execute('''
            UPDATE games
            SET num_copies = num_copies - %s
            WHERE id = %s
        ''', (num_copies, game_id))

        cursor.execute('SELECT num_copies FROM games WHERE id = %s', (game_id,))
        remaining_copies = cursor.fetchone()[0]
        conn.commit()
        return {'purchase_id': purchase_id, 'total_price': total_price, 'remaining_copies': remaining_copies,'purchase_date': purchase_date}
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_add_purchase", http_status=500).inc()
        raise BadRequest(f'Error while adding purchase: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_add_purchase", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_add_purchase").observe(time.time() - start_time)

def get_purchases(username):
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Recupera gli acquisti dell'utente specificato
        cursor.execute("""
            SELECT
                p.id AS purchase_id,
                u.username,
                g.title AS game_title,
                p.num_copies,
                g.price,
                p.purchase_date
            FROM
                purchases p
            JOIN
                all_users u ON p.user_id = u.id
            JOIN
                games g ON p.game_id = g.id
            WHERE
                u.username = %s
        """, (username,))

        purchases = cursor.fetchall()
        # Trasforma i risultati in una lista di dizionari
        purchase_list = [
            {
                'purchase_id': row[0],
                'username': row[1],
                'game_title': row[2],
                'num_copies': int(row[3]),
                'price': float(row[4]) if isinstance(row[4], Decimal) else row[4],
                'purchase_date': row[5]
            }
            for row in purchases
        ]

        return purchase_list
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_purchases", http_status=500).inc()
        raise BadRequest(f'Error while getting purchases: {str(e)}')
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_purchases", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_get_purchases").observe(time.time() - start_time)

def get_all_purchases():
    start_time = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Esegui una query per ottenere tutti gli acquisti con i dettagli
        cursor.execute("""
            SELECT 
                p.id AS purchase_id,
                u.username,
                g.title AS game_title,
                p.num_copies,
                g.price,
                p.purchase_date
            FROM 
                purchases p
            JOIN 
                all_users u ON p.user_id = u.id
            JOIN 
                games g ON p.game_id = g.id
            ORDER BY 
                p.purchase_date DESC
        """)

        # Recupera tutti i risultati
        purchases = cursor.fetchall()

        # Trasforma i risultati in un elenco di dizionari
        purchase_list = [
            {
                'purchase_id': row[0],
                'username': row[1],
                'game_title': row[2],
                'num_copies': row[3],
                'price': float(row[4]) if isinstance(row[4], Decimal) else row[4],
                'purchase_date': row[5]
            }
            for row in purchases
        ]

        return purchase_list
    except Exception as e:
        conn.rollback()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_all_purchases", http_status=500).inc()
        raise BadRequest(f"Error while retrieving purchases: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        DB_REQUEST_COUNT.labels(method="function_call", endpoint="postgres_get_all_purchases", http_status=200).inc()
        DB_REQUEST_LATENCY.labels(endpoint="postgres_get_all_purchases").observe(time.time() - start_time)
