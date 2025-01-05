from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import configparser
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

config = configparser.ConfigParser()
config.read('config.ini')

backend_url = config.get('backend', 'nginx_url')


def is_user_logged_in():
    return 'user' in session


def get_headers():
    """Restituisce gli header per le richieste, inclusi i dati di sessione."""
    return {
        'Token': session.get('token', ''),
        'ActualUser': session.get('user', '')
    }


def handle_request_error(response):
    if response.json().get('error', True):
        flash(response.json().get('message', 'Errore sconosciuto'))
        return redirect(url_for('home'))
    return response.json().get('message', {})


@app.route('/')
def home():
    if not is_user_logged_in():
        return redirect(url_for('login'))

    try:
        # Recupera i giochi preferiti dell'utente
        response_games = requests.get(f'{backend_url}/game-catalog/getUserPreferredGames', headers=get_headers())
        games = handle_request_error(response_games)

        # Recupera generi e filtra i giochi
        genres = list(set(game['genre'] for game in games))
        search_query = request.args.get('search', '')
        selected_genre = request.args.get('genre', '')

        if search_query:
            games = [game for game in games if search_query.lower() in game['title'].lower()]
        if selected_genre:
            games = [game for game in games if game['genre'] == selected_genre]

        # Notifiche non lette
        response_notifications = requests.get(f'{backend_url}/getUnreadNotifications/{session["user"]}')
        unread_notifications = response_notifications.json()

        return render_template('home.html', games=games, genres=genres, unread_notifications=unread_notifications)
    except Exception as e:
        flash(f'Errore durante il caricamento: {str(e)}')
        return redirect(url_for('login'))


@app.route('/game/<string:gameTitle>')
def game(gameTitle):
    response = requests.get(f'{backend_url}/getGameByTitle/{gameTitle}', headers=get_headers())
    game_data = handle_request_error(response)
    return render_template('game.html', game=game_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        credentials = request.form
        try:
            response = requests.post(f'{backend_url}/login', json=credentials)
            user_data = handle_request_error(response)
            session['user'] = user_data['email']
            session['token'] = user_data['token']
            return redirect(url_for('home'))
        except requests.exceptions.RequestException as e:
            flash(f'Login fallito: {str(e)}')
            return redirect(url_for('login'))
    return render_template('login.html')


# Endpoint per signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == 'POST':
        user_data = request.form
        try:
            # Simuliamo la richiesta al backend per il signup
            response = requests.post(f'{backend_url}/signup', json=user_data)
            if response.json()['error']:
                flash(response.json()['message'])
                return render_template('signup.html')
            response.raise_for_status()
            session['user'] = response.json()['user']
            session['token'] = response.json()['token']
            return redirect(url_for('home'))
        except requests.exceptions.HTTPError as http_err:
            flash('Signup failed: invalid credentials')
        except requests.exceptions.ConnectionError as conn_err:
            flash('Connection error: please try again later')
        except requests.exceptions.Timeout as timeout_err:
            flash('Request timed out: please try again later')
        except requests.exceptions.RequestException as req_err:
            flash('An unexpected error occurred: please try again later')
        return redirect(url_for('signup'))
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('token', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
