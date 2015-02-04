

def test_load(humongous):
    collection_names = humongous.collection_names()
    assert "players" in collection_names
    assert "championships" in collection_names
    check_players(humongous.players)
    check_championships(humongous.championships)


def check_players(players):
    assert players.count() == 2
    check_keys_in_docs(players, ["name", "surname", "position"])
    manuel = players.find_one({"name": "Manuel"})
    assert manuel["surname"] == "Neuer"
    assert manuel["position"] == "keeper"


def check_championships(championships):
    assert championships.count() == 3
    check_keys_in_docs(championships, ["year", "host", "winner"])


def check_keys_in_docs(collection, keys):
    for doc in collection.find():
        for key in keys:
            assert key in doc


def test_insert(humongous):
    humongous.players.insert({
        "name": "Bastian",
        "surname": "Schweinsteiger",
        "position": "midfield"
    })
    assert humongous.players.count() == 3
    assert humongous.players.find_one({"name": "Bastian"})
