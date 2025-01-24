CREATE TABLE IF NOT EXISTS all_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    num_copies INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES all_users(id) ON DELETE CASCADE,
    game_id INT REFERENCES games(id) ON DELETE CASCADE,
    num_copies INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES all_users(id) ON DELETE CASCADE,
    game_id INT REFERENCES games(id) ON DELETE CASCADE,
    num_copies INT NOT NULL CHECK (num_copies > 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO all_users (username, password, image_url)
VALUES ('admin', '$2b$12$SVFmb2K7Og5/ZitKuw4leOKqDXME5rcNRlRNIUG7z/onAessZ6GDO', 'https://static.vecteezy.com/system/resources/thumbnails/009/636/683/small_2x/admin-3d-illustration-icon-png.png') ON CONFLICT DO NOTHING;;

INSERT INTO games (title, num_copies, price)
VALUES
    ('dragon ball', 10, 69.99),
    ('bss', 97, 120.2),
    ('The Legend of Zelda: Breath of the Wild', 100, 59.99),
    ('The Witcher 3: Wild Hunt', 75, 49.99),
    ('Red Dead Redemption 2', 80, 69.99),
    ('Persona 5', 90, 39.99),
    ('Super Mario Odyssey', 85, 49.99),
    ('Cyberpunk 2077', 70, 59.99),
    ('God of War', 80, 49.99),
    ('The Last of Us Part II', 75, 59.99),
    ('Animal Crossing: New Horizons', 90, 49.99),
    ('Final Fantasy VII Remake', 80, 59.99),
    ('Mario Kart 8 Deluxe', 85, 49.99),
    ('Bloodborne', 70, 39.99),
    ('Hades', 90, 24.99),
    ('Sekiro: Shadows Die Twice', 75, 59.99),
    ('Ghost of Tsushima', 80, 49.99),
    ('Minecraft', 95, 29.99),
    ('Assassin''s Creed Valhalla', 75, 59.99),
    ('Pokémon Sword and Shield', 85, 59.99),
    ('Uncharted 4: A Thief''s End', 80, 39.99),
    ('Overwatch', 70, 39.99),
    ('The Elder Scrolls V: Skyrim', 85, 39.99),
    ('Death Stranding', 75, 49.99),
    ('Dark Souls III', 70, 39.99),
    ('Marvel''s Spider-Man', 80, 39.99),
    ('Horizon Zero Dawn', 84, 39.99),
    ('Final Fantasy XIV', 90, 29.99),
    ('NieR: Automata', 75, 49.99),
    ('Destiny 2', 80, 29.99),
    ('Demon''s Souls', 70, 69.99),
    ('Control', 75, 39.99),
    ('The Legend of Zelda: Skyward Sword HD', 85, 59.99),
    ('Bayonetta 2', 80, 49.99),
    ('Half-Life: Alyx', 70, 59.99);