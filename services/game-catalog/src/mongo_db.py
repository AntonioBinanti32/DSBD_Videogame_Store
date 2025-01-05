from pymongo import MongoClient

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

    def get_user_preferred_games_0(self, username):
        user_result = self.user_collection.find_one({"username": username})
        if not user_result:
            raise Exception("Errore durante il recupero dell'utente: Utente non trovato")

        reviews = user_result.get("reviews", [])
        preferred_genres = set()
        preferred_developers = set()

        for review in reviews:
            if review.get("rating", 0) >= 3:
                game_title = review.get("game_title")
                game_result = self.game_collection.find_one({"title": game_title})

                if game_result:
                    preferred_genres.add(game_result.get("genre", ""))
                    preferred_developers.add(game_result.get("developer", ""))

        # Filtra giochi basati sui generi e sviluppatori preferiti
        preferred_games_cursor = self.game_collection.find({
            "$or": [
                {"genre": {"$in": list(preferred_genres)}},
                {"developer": {"$in": list(preferred_developers)}}
            ]
        }, {"_id": 0})

        return list(preferred_games_cursor)

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
