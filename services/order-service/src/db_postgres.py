import jwt
import datetime
import psycopg2
import bcrypt
from werkzeug.exceptions import BadRequest
import os
import logging

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
    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.commit()
    cursor.close()
    conn.close()

# Funzione per effettuare il login
def login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

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

    return user

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT username, image_url FROM all_users WHERE username = %s', (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        raise BadRequest('User not found')

    return {'username': user[0], 'image_url': user[1]}