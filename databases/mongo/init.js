db = db.getSiblingDB('game-catalog'); // Seleziona il database 'game-catalog'

db.createCollection('games'); // Crea la collezione 'games' se non esiste

db.games.insertMany([
  {
    "_id": ObjectId("6665fb90a4fb25066b6207f2"),
    "title": "dragon ball",
    "genre": "genre",
    "release_date": new Date(-1000),
    "developer": "developer",
    "price": 69.99,
    "stock": 10,
    "description": "description",
    "image_url": "https://cdn11.bigcommerce.com/s-xs1cevxe43/images/stencil/1280x1280/attribute_rule_images/16068_source_1717799733.png",
    "reviews": [
      {
        "username": "antonio",
        "review_text": "test",
        "rating": 4,
        "created_at": new Date("2024-06-09T17:27:40.599Z")
      },
      {
        "username": "a",
        "review_text": "wow",
        "rating": 10,
        "created_at": new Date("2024-06-11T13:26:34.314Z")
      },
      {
        "username": "f",
        "review_text": "defrgv",
        "rating": 2,
        "created_at": new Date("2024-06-17T14:32:55.870Z")
      },
      {
        "username": "z",
        "review_text": "Great",
        "rating": 4,
        "created_at": new Date("2024-06-25T08:44:32.406Z")
      }
    ]
  },
  {
    "_id": ObjectId("66670e6eb31b2d055e43bc98"),
    "title": "bss",
    "genre": "TCG",
    "release_date": new Date("2024-08-14T23:00:00.000Z"),
    "developer": "Bandai",
    "price": 120.2,
    "stock": 97,
    "description": "The best",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQg8bCMLvXguA_W1ac7FIIs18JwBKsYsgLK5w&s"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2bd"),
    "title": "The Legend of Zelda: Breath of the Wild",
    "genre": "Action-adventure",
    "release_date": new Date("2017-03-03T00:00:00.000Z"),
    "developer": "Nintendo EPD",
    "price": 59.99,
    "stock": 100,
    "description": "An open-world action-adventure game set in the kingdom of Hyrule.",
    "image_url": "https://m.media-amazon.com/images/I/517lG2g5ZiL._AC_UF1000,1000_QL80_.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2be"),
    "title": "The Witcher 3: Wild Hunt",
    "genre": "Action RPG",
    "release_date": new Date("2015-05-19T00:00:00.000Z"),
    "developer": "CD Projekt Red",
    "price": 49.99,
    "stock": 75,
    "description": "A story-driven open world RPG set in a visually stunning fantasy universe.",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRLf2Em-HSjhelvKPoj7NQjpxgBWALxCAPdRw&s"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2bf"),
    "title": "Red Dead Redemption 2",
    "genre": "Action-adventure",
    "release_date": new Date("2018-10-26T00:00:00.000Z"),
    "developer": "Rockstar Studios",
    "price": 69.99,
    "stock": 80,
    "description": "An epic tale of life in America's unforgiving heartland.",
    "image_url": "https://upload.wikimedia.org/wikipedia/en/thumb/4/44/Red_Dead_Redemption_II.jpg/220px-Red_Dead_Redemption_II.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c0"),
    "title": "Persona 5",
    "genre": "JRPG",
    "release_date": new Date("2016-09-15T00:00:00.000Z"),
    "developer": "Atlus",
    "price": 39.99,
    "stock": 90,
    "description": "A role-playing video game developed by Atlus.",
    "image_url": "https://image.api.playstation.com/cdn/EP4062/CUSA06638_00/0fSaYhFhEVP183JLTwVec7qkzmaHNMS2.png"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c1"),
    "title": "Super Mario Odyssey",
    "genre": "Platformer",
    "release_date": new Date("2017-10-27T00:00:00.000Z"),
    "developer": "Nintendo EPD",
    "price": 49.99,
    "stock": 85,
    "description": "A 3D platformer featuring Mario and his new ally Cappy.",
    "image_url": "https://sm.ign.com/t/ign_it/image/e/e3-2017-su/e3-2017-super-mario-odyssey-hands-on-preview-a-brilliantly-b_zhsa.1280.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c2"),
    "title": "Cyberpunk 2077",
    "genre": "Action RPG",
    "release_date": new Date("2020-12-10T00:00:00.000Z"),
    "developer": "CD Projekt Red",
    "price": 59.99,
    "stock": 70,
    "description": "An open-world action-adventure story set in Night City.",
    "image_url": "https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c3"),
    "title": "God of War",
    "genre": "Action-adventure",
    "release_date": new Date("2018-04-20T00:00:00.000Z"),
    "developer": "Santa Monica Studio",
    "price": 49.99,
    "stock": 80,
    "description": "An action-adventure game that chronicles the journey of Kratos.",
    "image_url": "https://image.api.playstation.com/vulcan/ap/rnd/202207/1210/4xJ8XB3bi888QTLZYdl7Oi0s.png"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c4"),
    "title": "The Last of Us Part II",
    "genre": "Action-adventure",
    "release_date": new Date("2020-06-19T00:00:00.000Z"),
    "developer": "Naughty Dog",
    "price": 59.99,
    "stock": 75,
    "description": "A sequel to The Last of Us, an action-adventure game set in a post-apocalyptic world.",
    "image_url": "https://image.api.playstation.com/vulcan/ap/rnd/202311/1717/b3e5dd741258cd53af1f7d8b75406c07173c956567471757.png"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c5"),
    "title": "Animal Crossing: New Horizons",
    "genre": "Social simulation",
    "release_date": new Date("2020-03-20T00:00:00.000Z"),
    "developer": "Nintendo EPD",
    "price": 49.99,
    "stock": 90,
    "description": "A life simulation video game developed and published by Nintendo.",
    "image_url": "https://www.pokemonmillennium.net/wp-content/uploads/2020/03/copertina_animalcrossingcartridge.png"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c6"),
    "title": "Final Fantasy VII Remake",
    "genre": "Action RPG",
    "release_date": new Date("2020-04-10T00:00:00.000Z"),
    "developer": "Square Enix",
    "price": 59.99,
    "stock": 80,
    "description": "A remake of the 1997 PlayStation game Final Fantasy VII.",
    "image_url": "https://www.italiatopgames.it/wp-content/uploads/2019/09/405.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c7"),
    "title": "Mario Kart 8 Deluxe",
    "genre": "Kart racing",
    "release_date": new Date("2017-04-28T00:00:00.000Z"),
    "developer": "Nintendo EPD",
    "price": 49.99,
    "stock": 85,
    "description": "A kart racing video game featuring characters from the Mario series.",
    "image_url": "https://www.tomshw.it/storage/media/2023/11/5615/pass-mario-kart-8---copertina-BF23.png"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c8"),
    "title": "Bloodborne",
    "genre": "Action RPG",
    "release_date": new Date("2015-03-24T00:00:00.000Z"),
    "developer": "FromSoftware",
    "price": 39.99,
    "stock": 70,
    "description": "An action role-playing game developed by FromSoftware.",
    "image_url": "https://sm.ign.com/ign_it/game/b/bloodborne/bloodborne_8nrj.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2c9"),
    "title": "Hades",
    "genre": "Roguelike",
    "release_date": new Date("2020-09-17T00:00:00.000Z"),
    "developer": "Supergiant Games",
    "price": 24.99,
    "stock": 90,
    "description": "A roguelike dungeon crawler video game developed and published by Supergiant Games.",
    "image_url": "https://assetsio.gnwcdn.com/news-videogiochi-hades-disponibile-console-playstation-xbox-abbonati-xbox-game-pass-1628862573220.jpg?width=1200&height=1200&fit=crop&quality=100&format=png&enable=upscale&auto=webp"
  },
  {
  "_id": ObjectId("667eb250c0c0a40f5325d2ca"),
  "title": "Sekiro: Shadows Die Twice",
  "genre": "Action-adventure",
  "release_date": new Date("2019-03-22T00:00:00.000Z"),
  "developer": "FromSoftware",
  "price": 59.99,
  "stock": 75,
  "description": "An action-adventure game developed by FromSoftware.",
  "image_url": "https://p1.hiclipart.com/preview/197/514/344/sekiro-shadows-die-twice-icon-sekiro-shadows-die-twice-png-clipart-thumbnail.jpg",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2cb"),
  "title": "Ghost of Tsushima",
  "genre": "Action-adventure",
  "release_date": new Date("2020-07-17T00:00:00.000Z"),
  "developer": "Sucker Punch Productions",
  "price": 49.99,
  "stock": 80,
  "description": "An action-adventure game set in feudal Japan.",
  "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7n9u-kFJFMig8LiLEGjUgmadNo1SCpy3ouA&s",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2cc"),
  "title": "Minecraft",
  "genre": "Sandbox",
  "release_date": new Date("2011-11-18T00:00:00.000Z"),
  "developer": "Mojang Studios",
  "price": 29.99,
  "stock": 95,
  "description": "A sandbox video game developed by Mojang Studios.",
  "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRrhj9tTf4WFrWAqqpX0KXHZCtIoKkAfJkbXA&s",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2cd"),
  "title": "Assassin's Creed Valhalla",
  "genre": "Action-adventure",
  "release_date": new Date("2020-11-10T00:00:00.000Z"),
  "developer": "Ubisoft Montreal",
  "price": 59.99,
  "stock": 75,
  "description": "An action role-playing video game developed by Ubisoft.",
  "image_url": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/557703a2-f0df-4e9e-8006-f1a8a0666122/dedd7v9-b9238065-6651-4325-831f-5b36e5fa6bdb.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzU1NzcwM2EyLWYwZGYtNGU5ZS04MDA2LWYxYThhMDY2NjEyMlwvZGVkZDd2OS1iOTIzODA2NS02NjUxLTQzMjUtODMxZi01YjM2ZTVmYTZiZGIucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.XpvMEUWzDlEuIfWiuW9g2F6s3gdc7Osk32PN03UQmUU",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2ce"),
  "title": "Pokémon Sword and Shield",
  "genre": "RPG",
  "release_date": new Date("2019-11-15T00:00:00.000Z"),
  "developer": "Game Freak",
  "price": 59.99,
  "stock": 85,
  "description": "A role-playing video game developed by Game Freak and published by The Pokémon Company and Nintendo.",
  "image_url": "https://static1.srcdn.com/wordpress/wp-content/uploads/2021/09/Pok--mon-Sword-Shield-Snoo-Reddit.jpg",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2cf"),
  "title": "Uncharted 4: A Thief's End",
  "genre": "Action-adventure",
  "release_date": new Date("2016-05-10T00:00:00.000Z"),
  "developer": "Naughty Dog",
  "price": 39.99,
  "stock": 80,
  "description": "An action-adventure game developed by Naughty Dog.",
  "image_url": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/4d04d46d-481e-452a-9bfd-75a8c1cc65a3/dfhe8il-908ca101-83b9-4d22-8e17-4ccd76c40a79.png",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d0"),
  "title": "Overwatch",
  "genre": "First-person shooter",
  "release_date": new Date("2016-05-24T00:00:00.000Z"),
  "developer": "Blizzard Entertainment",
  "price": 39.99,
  "stock": 70,
  "description": "A team-based multiplayer first-person shooter developed and published by Blizzard Entertainment.",
  "image_url": "https://upload.wikimedia.org/wikipedia/en/5/51/Overwatch_cover_art.jpg",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d1"),
  "title": "The Elder Scrolls V: Skyrim",
  "genre": "Action RPG",
  "release_date": new Date("2011-11-11T00:00:00.000Z"),
  "developer": "Bethesda Game Studios",
  "price": 39.99,
  "stock": 85,
  "description": "An action role-playing game developed by Bethesda Game Studios.",
  "image_url": "https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d2"),
  "title": "Death Stranding",
  "genre": "Action",
  "release_date": new Date("2019-11-08T00:00:00.000Z"),
  "developer": "Kojima Productions",
  "price": 49.99,
  "stock": 75,
  "description": "An action game developed by Kojima Productions.",
  "image_url": "https://a.storyblok.com/f/178900/640x360/dd580a03cd/385b98fc08d03cb3d5de8fcd2bdc32891563804831_full.png/m/640x360",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d3"),
  "title": "Dark Souls III",
  "genre": "Action RPG",
  "release_date": new Date("2016-04-12T00:00:00.000Z"),
  "developer": "FromSoftware",
  "price": 39.99,
  "stock": 70,
  "description": "An action role-playing game developed by FromSoftware.",
  "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8TX2ZQ3Q0mwJl6lF1lMa3EHNf5ibGfqvyxg&s",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d4"),
  "title": "Marvel's Spider-Man",
  "genre": "Action-adventure",
  "release_date": new Date("2018-09-07T00:00:00.000Z"),
  "developer": "Insomniac Games",
  "price": 39.99,
  "stock": 80,
  "description": "An action-adventure game based on the Marvel Comics superhero Spider-Man.",
  "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ6jiJdVwM2gG7yYgKqZgf3DwgGGeoMLR01w&s",
  "reviews": []
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d5"),
  "title": "Horizon Zero Dawn",
  "genre": "Action RPG",
  "release_date": new Date("2017-02-28T00:00:00.000Z"),
  "developer": "Guerrilla Games",
  "price": 39.99,
  "stock": 84,
  "description": "An action role-playing game developed by Guerrilla Games.",
  "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTdoXfFw3V2lAH6W7MLPQgxPEHGhRjZ-iHtyg&s",
  "reviews": [
    {
      "username": "admin",
      "review_text": "Great",
      "rating": 4,
      "created_at": new Date("2024-07-14T18:19:49.618Z")
    }
  ]
},
{
  "_id": ObjectId("667eb250c0c0a40f5325d2d6"),
  "title": "Final Fantasy XIV",
  "genre": "MMORPG",
  "release_date": new Date("2010-09-30T00:00:00.000Z"),
  "developer": "Square Enix",
  "price": 29.99,
  "stock": 90,
  "description": "A massively multiplayer online role-playing game developed by Square Enix.",
  "image_url": "https://cdn11.bigcommerce.com/s-kqbs9oimhc/images/stencil/1280x1280/products/2600/13957/FFXIV_DT_Agnostic_Packshot_Standard_Edition_1000x1436_EN_v1__62092.1711355937.jpg?c=1",
  "reviews": []
},
{
    "_id": ObjectId("667eb250c0c0a40f5325d2d7"),
    "title": "NieR: Automata",
    "genre": "Action RPG",
    "release_date": new Date("2017-02-23T00:00:00.000Z"),
    "developer": "PlatinumGames",
    "price": 49.99,
    "stock": 75,
    "description": "An action role-playing game developed by PlatinumGames.",
    "image_url": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/48192ce8-2589-4a6e-83a8-4363db9a5889/dbdg0kr-9eae1149-9548-4a4d-a758-615c97aef25e.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzQ4MTkyY2U4LTI1ODktNGE2ZS04M2E4LTQzNjNkYjlhNTg4OVwvZGJkZzBrci05ZWFlMTE0OS05NTQ4LTRhNGQtYTc1OC02MTVjOTdhZWYyNWUucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.suSmnL0zSq0m9wqRBYCwXVM_2YKaEjzA8-z4RM4wyN0"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2d8"),
    "title": "Destiny 2",
    "genre": "First-person shooter",
    "release_date": new Date("2017-09-06T00:00:00.000Z"),
    "developer": "Bungie",
    "price": 29.99,
    "stock": 80,
    "description": "A multiplayer first-person shooter video game developed by Bungie.",
    "image_url": "https://sm.ign.com/t/ign_it/screenshot/default/packshots-2d-pc_up49.1080.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2d9"),
    "title": "Demon's Souls",
    "genre": "Action RPG",
    "release_date": new Date("2020-11-12T00:00:00.000Z"),
    "developer": "Bluepoint Games / Japan Studio",
    "price": 69.99,
    "stock": 70,
    "description": "A remake of the original Demon's Souls.",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSM8AvxdF0RG6MFvAuUeJGKzWoPz4N1s3-coQ&s"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2da"),
    "title": "Control",
    "genre": "Action-adventure",
    "release_date": new Date("2019-08-27T00:00:00.000Z"),
    "developer": "Remedy Entertainment",
    "price": 39.99,
    "stock": 75,
    "description": "An action-adventure video game developed by Remedy Entertainment.",
    "image_url": "https://image.api.playstation.com/vulcan/ap/rnd/202008/2111/hvVTsd8akckaGtN2eZ3yIuwc.png"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2db"),
    "title": "The Legend of Zelda: Skyward Sword HD",
    "genre": "Action-adventure",
    "release_date": new Date("2021-07-16T00:00:00.000Z"),
    "developer": "Nintendo EPD",
    "price": 59.99,
    "stock": 85,
    "description": "An action-adventure game and the sixteenth main installment in The Legend of Zelda series.",
    "image_url": "https://assets-prd.ignimgs.com/2021/02/23/zelda-skyward-sword-hd-button-1614064616471.jpg"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2dc"),
    "title": "Bayonetta 2",
    "genre": "Action",
    "release_date": new Date("2014-09-20T00:00:00.000Z"),
    "developer": "PlatinumGames",
    "price": 49.99,
    "stock": 80,
    "description": "An action game developed by PlatinumGames.",
    "image_url": "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/9223f636-4088-439b-b879-a939912979c4/deiildu-64dbac44-87f9-4eb6-bcfd-1e148142a16b.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzkyMjNmNjM2LTQwODgtNDM5Yi1iODc5LWE5Mzk5MTI5NzljNFwvZGVpaWxkdS02NGRiYWM0NC04N2Y5LTRlYjYtYmNmZC0xZTE0ODE0MmExNmIucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.s2ycrSNuowJ_Q2s8YXe0DRH2-tmLlJC8OxmwdpODMh8"
  },
  {
    "_id": ObjectId("667eb250c0c0a40f5325d2dd"),
    "title": "Half-Life: Alyx",
    "genre": "VR First-person shooter",
    "release_date": new Date("2020-03-23T00:00:00.000Z"),
    "developer": "Valve",
    "price": 59.99,
    "stock": 70,
    "description": "A virtual reality (VR) first-person shooter developed and published by Valve.",
    "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSLYqB4zuPhphrst04rTHIhVSa1eLIPlRgXSg&s"
  }
]);
