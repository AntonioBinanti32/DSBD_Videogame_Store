from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)


def convert_to_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DD")

class MongoDB:
    _instance = None

    @staticmethod
    def get_instance():
        if MongoDB._instance is None:
            MongoDB._instance = MongoDB()
        return MongoDB._instance

    def __init__(self):
        from main import client, db
        self.client = client
        self.db = db
        self.user_collection = self.db["users"]
        self.game_collection = self.db["games"]

    def get_all_users(self):
        usernames_cursor = self.user_collection.find({}, {"_id": 0, "username": 1})
        usernames = [user['username'] for user in usernames_cursor]
        return usernames

    def get_user_preferred_games(self, username):
        try:
            # Recupera l'utente
            user_result = self.user_collection.find_one({"username": username})
            if not user_result:
                raise Exception("Errore durante il recupero dell'utente: Utente non trovato")

            # Estrai i dati dell'utente
            user = user_result
            reviews = user.get("reviews", [])
            purchases = user.get("purchases", [])

            # Set per generi e sviluppatori preferiti
            preferred_genres = set()
            preferred_developers = set()

            # Identifica i generi e sviluppatori preferiti in base alle recensioni
            for review in reviews:
                if review.get("rating", 0) >= 3:
                    game_title = review.get("game_title")
                    game_result = self.game_collection.find_one({"title": game_title})
                    if game_result:
                        preferred_genres.add(game_result.get("genre", ""))
                        preferred_developers.add(game_result.get("developer", ""))

            # Identifica i generi e sviluppatori preferiti in base agli acquisti
            for purchase in purchases:
                game_title = purchase.get("game_title")
                game_result = self.game_collection.find_one({"title": game_title})
                if game_result:
                    preferred_genres.add(game_result.get("genre", ""))
                    preferred_developers.add(game_result.get("developer", ""))

            # Recupera tutti i giochi
            games_cursor = self.game_collection.find({}, {"_id": 0})
            games = []

            for game_result in games_cursor:
                # Aggiungi un punteggio di preferenza per ogni gioco
                preference_score = 0
                genre = game_result.get("genre", "")
                developer = game_result.get("developer", "")

                if genre in preferred_genres:
                    preference_score += 10
                if developer in preferred_developers:
                    preference_score += 10

                # Aggiungi il punteggio al gioco
                game_result["preferenceScore"] = preference_score
                games.append(game_result)

            # Ordina i giochi in base al punteggio di preferenza
            games.sort(key=lambda x: x.get("preferenceScore", 0), reverse=True)

            return games

        except Exception as e:
            raise Exception("Errore durante il recupero dei giochi preferiti dell'utente: " + str(e))

    def get_game_by_title(self, title):
        try:
            game_result = self.game_collection.find_one({"title": title})
            if not game_result:
                raise Exception("Errore durante il recupero del gioco: Gioco non trovato")
            game_result["_id"] = str(game_result["_id"])
            return game_result
        except Exception as e:
            raise Exception("Errore durante il recupero del gioco: " + str(e))

    def add_game(self, title, genre, release_date, developer, price, stock, description, image_url, reviews=None):

        doc = {
            "title": title,
            "genre": genre,
            "release_date": convert_to_date(release_date),
            "developer": developer,
            "price": price,
            "stock": stock,
            "description": description,
            "image_url": image_url,
            "reviews": reviews if reviews else []
        }

        try:
            game_result = self.game_collection.find_one({"title": title})
            if game_result:
                raise Exception("Errore durante la creazione del gioco: Gioco già esistente nel catalogo")
            game_added = self.game_collection.insert_one(doc)
            game_added_doc = game_added.inserted_id
            if game_added_doc:
                doc["_id"] = str(game_added_doc)
                return doc
        except PyMongoError as e:
            raise Exception("Errore durante l'aggiunta del gioco") from e

    def update_game(self, title, updates):
        try:
            game_result = self.game_collection.find_one({"title": title})
            if not game_result:
                raise Exception("Errore durante l'aggiornamento: Gioco non trovato nel catalogo")

            if 'release_date' in updates:
                updates['release_date'] = convert_to_date(updates['release_date'])
            updated_result = self.game_collection.update_one(
                {"title": title}, {"$set": updates}
            )

            if updated_result.modified_count == 0:
                raise Exception("Errore durante l'aggiornamento: Nessuna modifica effettuata")

            updated_game = self.game_collection.find_one({"title": title})
            updated_game["_id"] = str(updated_game["_id"])
            return updated_game
        except PyMongoError as e:
            raise Exception("Errore durante l'aggiornamento del gioco") from e

    def delete_game(self, title):
        try:
            game_result = self.game_collection.find_one({"title": title})
            if not game_result:
                raise Exception("Errore durante l'eliminazione: Gioco non trovato nel catalogo")

            delete_result = self.game_collection.delete_one({"title": title})
            if delete_result.deleted_count == 0:
                raise Exception("Errore durante l'eliminazione: Nessuna modifica effettuata")

            game_result2 = self.game_collection.find_one({"title": title})
            if not game_result2:
                return True
        except PyMongoError as e:
            raise Exception("Errore durante l'eliminazione del gioco") from e

    def add_review(self, username, game_title, review_text, rating):
        try:
            game_doc = self.game_collection.find_one({"title": game_title})
            if not game_doc:
                raise Exception("Gioco non trovato")

            game_id = game_doc["_id"]

            user_doc = self.user_collection.find_one({"username": username})
            if not user_doc:
                raise Exception("Utente non trovato")

            user_id = user_doc["_id"]

            query = {
                "$and": [
                    {"reviews.game_title": game_title},
                    {"username": username}
                ]
            }

            existing_review = self.user_collection.find_one(query)
            if existing_review:
                raise Exception("Il gioco è già stato recensito da questo utente")

            review_doc = {
                "username": username,
                "review_text": review_text,
                "rating": rating,
                "created_at": datetime.utcnow()
            }

            # Aggiunge la recensione al gioco
            self.game_collection.update_one(
                {"_id": game_id},
                {"$push": {"reviews": review_doc}}
            )

            # Aggiunge la recensione all'utente
            user_review_doc = {
                "game_title": game_title,
                "review_text": review_text,
                "rating": rating,
                "created_at": datetime.utcnow()
            }

            self.user_collection.update_one(
                {"_id": user_id},
                {"$push": {"reviews": user_review_doc}}
            )

            return True

        except Exception as e:
            raise e
        except PyMongoError as e:
            raise Exception("Errore durante l'aggiunta della recensione") from e

    def get_review_by_game(self, title):
        try:
            game_result = self.game_collection.find_one({"title": title})
            if not game_result:
                raise Exception("Errore durante il recupero del gioco: Gioco non trovato")
            reviews = game_result.get("reviews", [])
            if not reviews:
                raise Exception("Non ci sono recensioni per questo gioco")
            return reviews
        except Exception as e:
            raise e
        except PyMongoError as e:
            raise Exception("Errore durante il recupero delle recensioni") from e
