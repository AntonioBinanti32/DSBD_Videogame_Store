from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import configparser
from datetime import datetime
import json
import logging
import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

config = configparser.ConfigParser()
config.read('config.ini')

backend_url = config.get('backend', 'nginx_url')

def is_user_logged_in():
    return 'user' in session

def is_admin():
    if session['user'] == 'admin':
            return True
    else:
        return False

def getHeaders():
    user = session.get('user')
    token = session.get('token')

    headers = {
        'Token': token,
        'ActualUser': user
    }

    return headers

def convertToJson(message_str):
    try:
        message = json.loads(message_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Impossibile decodificare il JSON da 'message': {e}")
    return message

def getUserInformation():
    user = session.get('user')
    response_user = requests.get(f'{backend_url}/order-service/getUser/{user}', headers=getHeaders())
    if response_user.status_code == 200:
        return response_user.json()['user']
    else:
        logger.error(f"Failed to retrieve user information. Status Code: {response_user.status_code}")
        return None

"""
@app.template_filter('dateformat')
def dateformat(value):
    try:
        if isinstance(value, (int, float)):
            # Se il valore è un timestamp Unix, convertilo in datetime
            dt_object = datetime.utcfromtimestamp(value / 1000.0)
        elif isinstance(value, dict) and '$date' in value:
            # Se il valore è un oggetto data MongoDB
            dt_object = datetime.utcfromtimestamp(value['$date'] / 1000.0)
        else:
            raise ValueError("Formato data non riconosciuto")

        # Formatta la data come desiderato (es. "%Y-%m-%d %H:%M:%S")
        formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date
    except Exception as e:
        print(f"Errore nella formattazione del timestamp: {e}")
        return "Data non disponibile"
"""

@app.template_filter('dateformat')
def dateformat(value):
    try:
        if isinstance(value, (int, float)):
            # Se il valore è un timestamp Unix, convertilo in datetime
            dt_object = datetime.utcfromtimestamp(value / 1000.0)
        elif isinstance(value, dict) and '$date' in value:
            # Se il valore è un oggetto data MongoDB
            dt_object = datetime.utcfromtimestamp(value['$date'] / 1000.0)
        elif isinstance(value, str):
            # Se il valore è una stringa, prova a convertirla in datetime
            dt_object = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z")
        else:
            raise ValueError("Formato data non riconosciuto")

        # Formatta la data come desiderato (es. "%Y-%m-%d %H:%M:%S")
        formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date
    except Exception as e:
        print(f"Errore nella formattazione del timestamp: {e}")
        return "Data non disponibile"

@app.template_filter('dateformat_input')
def dateformat_input(value):
    try:
        if isinstance(value, dict) and '$date' in value:
            # Se il valore è un oggetto data MongoDB
            dt_object = datetime.utcfromtimestamp(value['$date'] / 1000.0)
        else:
            raise ValueError("Formato data non riconosciuto")

        # Formatta la data come richiesto per l'input di tipo 'date'
        formatted_date = dt_object.strftime("%Y-%m-%d")
        return formatted_date
    except Exception as e:
        print(f"Errore nella formattazione del timestamp per input: {e}")
        return ""


@app.route('/')
def home():
    try:
        if not is_user_logged_in():
            return redirect(url_for('login'))
        actualUser = getUserInformation()
        response_games = requests.get(f'{backend_url}/game-catalog/getUserPreferredGames', headers=getHeaders())
        if response_games.status_code == 204:
            return render_template('home.html', games=[], genres=[], actualUser=[], admin=False,
                                   unread_notifications=[])
        elif response_games.status_code != 200:
            flash(response_games.json()['message'])
            return render_template('home.html', games=[], genres=[], actualUser=[], admin=False,
                                   unread_notifications=[])
        games = response_games.json()['message']

        # Recupera i parametri di ricerca e filtro dalla richiesta
        search_query = request.args.get('search', '')
        selected_genre = request.args.get('genre', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        sort_order = request.args.get('sort_order', '')

        # Filtra i giochi in base alla ricerca
        if search_query:
            games = [game for game in games if search_query.lower() in game['title'].lower()]

        # Filtra i giochi in base al genere
        if selected_genre:
            games = [game for game in games if game['genre'] == selected_genre]

        # Filtra i giochi in base al prezzo
        if min_price:
            games = [game for game in games if game['price'] >= float(min_price)]
        if max_price:
            games = [game for game in games if game['price'] <= float(max_price)]

        # Ordinamento dei giochi
        if sort_order == 'title':
            games = sorted(games, key=lambda x: x['title'])
        elif sort_order == 'genre':
            games = sorted(games, key=lambda x: x['genre'])
        elif sort_order == 'developer':
            games = sorted(games, key=lambda x: x['developer'])
        elif sort_order == 'preferred':
            response_preferred_games = requests.get(f'{backend_url}/game-catalog/getUserPreferredGames', headers=getHeaders())
            preferred_games = response_preferred_games.json()['message']
            games = preferred_games

        # Recupera i generi dei giochi
        genres = list(set(game['genre'] for game in games))

        username = session.get('user')
        response_notifications = requests.get(f'{backend_url}/notification-service/getUnreadNotifications/{username}', headers=getHeaders())
        if response_notifications.status_code != 200:
            raise flash(response_notifications.json()['message'])
            return redirect(url_for('home'))
        unread_notifications = response_notifications.json()['unread_notifications']
        if unread_notifications is None:
            return render_template('home.html', games=games, genres=genres, actualUser=actualUser, admin=is_admin(),
                                   unread_notifications=[])

        return render_template('home.html', games=games, genres=genres, actualUser=actualUser, admin=is_admin(),
                               unread_notifications=unread_notifications)
    except requests.exceptions.HTTPError as http_err:
        flash('Login failed: invalid credentials')
    except requests.exceptions.ConnectionError as conn_err:
        flash('Connection error: please try again later')
    except requests.exceptions.Timeout as timeout_err:
        flash('Request timed out: please try again later')
    except requests.exceptions.RequestException as req_err:
        flash('An unexpected error occurred: please try again later')
    return redirect(url_for('login'))


@app.route('/game/<string:gameTitle>')
def game(gameTitle):
    response = requests.get(f'{backend_url}/game-catalog/getGameByTitle/{gameTitle}', headers = getHeaders())
    if response.status_code != 200:
        flash(response.json()['message'])
        return redirect(url_for('home'))
    game = response.json()['game']
    return render_template('game.html', game=game, admin=is_admin())

@app.route('/create_game', methods=['GET', 'POST'])
def create_game():
    if request.method == 'POST':

        data = {
            'title': request.form['title'],
            'genre': request.form['genre'],
            'releaseDate': request.form['releaseDate'],
            'developer': request.form['developer'],
            'price': float(request.form['price']),
            'stock': int(request.form['stock']),
            'description': request.form['description'],
            'imageUrl': request.form['imageUrl']
        }

        try:
            response = requests.post(f'{backend_url}/game-catalog/addGame', json=data, headers=getHeaders())
            if response.status_code != 200:
                flash(response.json()['message'])
                return redirect(url_for('home'))
            response.raise_for_status()
            flash('Game created successfully!', 'success')
            return redirect(url_for('home'))
        except requests.exceptions.RequestException as e:
            flash(f"Failed to create game: {e}", 'danger')
            return redirect(url_for('create_game'))
    return render_template('create_game.html')


@app.route('/update_game/<string:gameTitle>', methods=['GET'])
def update_game_form(gameTitle):
    if not is_admin():
        flash('Only admin users can update games.', 'danger')
        return redirect(url_for('home'))

    # Recupera i dettagli del gioco per il form di aggiornamento
    response = requests.get(f'{backend_url}/game-catalog/getGameByTitle/{gameTitle}', headers=getHeaders())
    if response.status_code != 200:
        flash(response.json()['message'])
        return redirect(url_for('home'))
    game = response.json()['game']

    return render_template('update_game.html', game=game)


@app.route('/update_game/<string:gameTitle>', methods=['POST'])
def update_game(gameTitle):
    if not is_admin():
        flash('Only admin users can update games.', 'danger')
        return redirect(url_for('home'))

    update_data = {
        'title': gameTitle,
        'newGenre': request.form['newGenre'],
        'newReleaseDate': request.form['newReleaseDate'],
        'newDeveloper': request.form['newDeveloper'],
        'newPrice': float(request.form['newPrice']),
        'newStock': int(request.form['newStock']),
        'newDescription': request.form['newDescription'],
        'newImageUrl': request.form['newImageUrl']
    }

    try:
        response = requests.put(f'{backend_url}/game-catalog/updateGame', json=update_data, headers=getHeaders())
        if response.status_code != 200:
            flash(response.json()['message'])
            return redirect(url_for('home'))
        response.raise_for_status()
        flash('Game updated successfully!', 'success')
    except requests.exceptions.RequestException as e:
        flash(f"Failed to update game: {str(e)}", 'danger')

    return redirect(url_for('game', gameTitle=gameTitle))


@app.route('/delete_game/<string:gameTitle>', methods=['POST'])
def delete_game(gameTitle):
    if not is_admin():
        flash('Only admin users can delete games.', 'danger')
        return redirect(url_for('home'))

    try:
        response = requests.delete(f'{backend_url}/game-catalog/deleteGame/{gameTitle}', headers=getHeaders())
        if response.status_code != 200:
            flash(response.json()['message'])
            return redirect(url_for('home'))
        response.raise_for_status()
        flash('Game deleted successfully!', 'success')
    except requests.exceptions.RequestException as e:
        flash(f"Failed to delete game: {str(e)}", 'danger')

    return redirect(url_for('home'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    logger.info(f"\n\n\nURL: {backend_url}\n\n\n")
    if request.method == 'POST':
        credentials = request.form
        try:
            response = requests.post(f'{backend_url}/order-service/login', json=credentials)
            if response.status_code != 200:
                flash(response.json()['message'])
                return render_template('login.html')
            response.raise_for_status()  # Questo genera un'eccezione per codici di stato HTTP 4xx/5xx
            session['user'] = response.json()['user']
            session['token'] = response.json()['token']
            user = getUserInformation()
            session['user_image'] = user['image_url']
            return redirect(url_for('home'))
        except requests.exceptions.HTTPError as http_err:
            flash('Login failed: invalid credentials')
        except requests.exceptions.ConnectionError as conn_err:
            flash('Connection error: please try again later')
        except requests.exceptions.Timeout as timeout_err:
            flash('Request timed out: please try again later')
        except requests.exceptions.RequestException as req_err:
            flash('An unexpected error occurred: please try again later')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_data = request.form
        try:
            response = requests.post(f'{backend_url}/order-service/signup', json=user_data)
            if response.status_code != 200:
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


@app.route('/reviews/<string:gameTitle>', methods=['GET', 'POST'])
def reviews(gameTitle):
    if request.method == 'POST':
        review_text = request.form.get('review')
        rating = int(request.form.get('rating'))
        username = session.get('user')
        review_data = {
            'username': username,
            'gameTitle': gameTitle,
            'reviewText': review_text,
            'rating': rating
        }

        headers = getHeaders()
        try:
            response = requests.post(f'{backend_url}/game-catalog/addReview', json=review_data, headers=headers)
            if response.status_code != 200:
                flash(response.json()['message'])
                return redirect(url_for('game', gameTitle=gameTitle))
            response.raise_for_status()
            flash('Review added successfully!', 'success')
        except requests.exceptions.RequestException as e:
            flash(f"Failed to add review: you can isert only one review for a game.", 'danger')

        return redirect(url_for('game', gameTitle=gameTitle))

    else:
        # Metodo GET per ottenere le recensioni già presenti
        response = requests.get(f'{backend_url}/game-catalog/getReviewByGame/{gameTitle}')
        if response.status_code != 200:
            flash(response.json()['message'])
            return redirect(url_for('game', gameTitle=gameTitle))
        reviews = response.json()['reviews']
        return render_template('game.html', gameTitle=gameTitle, admin=is_admin())
    return render_template('game.html', gameTitle=gameTitle, admin=is_admin())

@app.route('/cart', methods = ['GET'])
def cart():
    try:
        if not is_user_logged_in():
            return redirect(url_for('login'))

        username = session.get('user')
        response = requests.get(f'{backend_url}/order-service/getReservations/{username}', headers=getHeaders())
        if response.status_code != 200:
            flash(response.json()['message'])
            return redirect(url_for('home'))
        response.raise_for_status()
        cart_items = response.json()['reservations']
        return render_template('cart.html', cart_items=cart_items, admin=is_admin())
    except requests.exceptions.HTTPError as http_err:
        flash('Failed to fetch cart: invalid credentials')
    except requests.exceptions.ConnectionError as conn_err:
        flash('Connection error: please try again later')
    except requests.exceptions.Timeout as timeout_err:
        flash('Request timed out: please try again later')
    except requests.exceptions.RequestException as req_err:
        flash('An unexpected error occurred: please try again later')
    return redirect(url_for('home'))

@app.route('/add_to_cart/<string:gameTitle>', methods=['GET', 'POST'])
def add_to_cart(gameTitle):
    if not is_user_logged_in():
        return redirect(url_for('login'))

    quantity = int(request.form.get('quantity'))
    username = session.get('user')
    review_data = {
        'username': username,
        'gameTitle': gameTitle,
        'numCopies': quantity
    }
    try:
        response = requests.post(f'{backend_url}/order-service/addReservation', headers = getHeaders(), json=review_data)
        if response.status_code != 200:
            flash(response.json()['message'])
            return redirect(url_for('game', gameTitle=gameTitle))
        response.raise_for_status()
        flash('Game added successfully to cart!', 'success')
    except requests.exceptions.RequestException as e:
        flash(f"Failed to add game in cart: {str(e)}", 'danger')

    return redirect(url_for('game', gameTitle=gameTitle))


@app.route('/remove_from_cart/<string:reservation_id>', methods=['POST'])
def remove_from_cart(reservation_id):
    try:
        if not is_user_logged_in():
            return redirect(url_for('login'))

        if not reservation_id.isalnum():
            flash('Invalid reservation ID', 'danger')
            return redirect(url_for('cart'))


        response = requests.delete(f'{backend_url}/order-service/deleteReservation/{reservation_id}', headers=getHeaders())
        if response.status_code != 200:
            flash(response.json()['message'])
            return redirect(url_for('cart'))
        response.raise_for_status()

        flash('Game removed from cart successfully!', 'success')
    except requests.exceptions.HTTPError as http_err:
        flash('Failed to remove game from cart: invalid credentials', 'danger')
    except requests.exceptions.ConnectionError as conn_err:
        flash('Connection error: please try again later', 'danger')
    except requests.exceptions.Timeout as timeout_err:
        flash('Request timed out: please try again later', 'danger')
    except requests.exceptions.RequestException as req_err:
        flash('An unexpected error occurred: please try again later', 'danger')

    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        if not is_user_logged_in():
            return redirect(url_for('login'))

        if request.method == 'POST':
            cart_items = request.form.get('cart_items')
            if cart_items:
                cart_items = json.loads(cart_items)

            if not cart_items:
                flash('Your cart is empty.', 'danger')
                return redirect(url_for('cart'))

            username = session.get('user')
            # Loop through each item in the cart and create a purchase request
            for item in cart_items:
                purchase_data = {
                    'username': username,
                    'gameTitle': item['game_title'],
                    'numCopies': item['num_copies']
                }
                response = requests.post(f'{backend_url}/order-service/addPurchase', json=purchase_data, headers=getHeaders())
                if response.status_code != 200:
                    flash(response.json()['message'])
                    return redirect(url_for('cart'))
                response.raise_for_status()

                # After successfully adding the purchase, remove the item from the cart
                reservation_id = item['_id']
                remove_response = requests.delete(f'{backend_url}/order-service/deleteReservation/{reservation_id}', headers=getHeaders())
                if response.status_code != 200:
                    flash(response.json()['message'])
                    return redirect(url_for('cart'))
                remove_response.raise_for_status()

            flash('Order placed successfully!', 'success')
            return redirect(url_for('checkout'))

        else:  # GET request
            username = session.get('user')
            response = requests.get(f'{backend_url}/order-service/getPurchases/{username}', headers=getHeaders())
            if response.status_code != 200:
                flash(response.json()['message'])
                return redirect(url_for('cart'))
            response.raise_for_status()
            purchases = response.json()['purchases']
            return render_template('checkout.html', purchases=purchases, admin=is_admin())

    except requests.exceptions.RequestException as e:
        flash('An error occurred while processing your request. Please try again later.', 'danger')
        return redirect(url_for('cart'))


@app.route('/purchases', methods=['GET'])
def purchases():
    try:
        if not is_admin():
            flash('Only admin users can view all purchases.', 'danger')
            return redirect(url_for('home'))

        response = requests.get(f'{backend_url}/order-service/getAllPurchases', headers=getHeaders())
        if response.json()['error']:
            flash(response.json()['message'])
            return redirect(url_for('home'))
        response.raise_for_status()
        purchases = response.json()['purchases']

        total_revenue = sum(item['num_copies'] * item['price'] for item in purchases)

        return render_template('purchases.html', purchases=purchases, total_revenue=total_revenue, admin=is_admin())
    except requests.exceptions.HTTPError as http_err:
        flash('Failed to fetch purchases: invalid credentials')
    except requests.exceptions.ConnectionError as conn_err:
        flash('Connection error: please try again later')
    except requests.exceptions.Timeout as timeout_err:
        flash('Request timed out: please try again later')
    except requests.exceptions.RequestException as req_err:
        flash('An unexpected error occurred: please try again later')
    return redirect(url_for('home'))

@app.route('/notifications', methods=['GET'])
def notifications():
    try:
        if not is_user_logged_in():
            return redirect(url_for('login'))

        username = session.get('user')

        response_2 = requests.get(f'{backend_url}/notification-service/getAllNotifications/{username}', headers=getHeaders())
        response_2.raise_for_status()
        notifications = response_2.json()["notifications"]
        response_3 = requests.get(f'{backend_url}/notification-service/getUnreadNotifications/{username}', headers=getHeaders())
        response_3.raise_for_status()
        notifications_unread = response_3.json()["unread_notifications"]

        return render_template('notifications.html', notifications=notifications, notifications_unread=notifications_unread)
    except requests.exceptions.HTTPError as http_err:
        flash('Failed to fetch notifications: invalid credentials')
    except requests.exceptions.ConnectionError as conn_err:
        flash('Connection error: please try again later')
    except requests.exceptions.Timeout as timeout_err:
        flash('Request timed out: please try again later')
    except requests.exceptions.RequestException as req_err:
        flash('An unexpected error occurred: please try again later')
    return redirect(url_for('home'))


@app.route('/mark_as_read/<int:notification_id>', methods=['POST'])
def mark_as_read(notification_id):
    try:

        if not is_user_logged_in():
            return redirect(url_for('login'))

        username = session.get('user')
        data = {
            'NotificationID': notification_id,
            'Username': username
        }
        response = requests.post(f'{backend_url}/notification-service/markNotificationAsRead', json=data, headers=getHeaders())
        response.raise_for_status()
        return redirect(url_for('notifications', username=username))

    except requests.exceptions.HTTPError as http_err:
        flash(f'Failed to mark notifications: invalid credentials- {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        flash('Connection error: please try again later')
    except requests.exceptions.Timeout as timeout_err:
        flash('Request timed out: please try again later')
    except requests.exceptions.RequestException as req_err:
        flash('An unexpected error occurred: please try again later')
    return redirect(url_for('notifications'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)