from pytest_mongodb import plugin


def test_load(mongodb):
    collection_names = mongodb.list_collection_names()
    assert 'players' in collection_names
    assert 'championships' in collection_names
    assert len(plugin._cache.keys()) == 2
    check_players(mongodb.players)
    check_championships(mongodb.championships)


def check_players(players):
    assert players.count_documents({}) == 2
    check_keys_in_docs(players, ['name', 'surname', "position"])
    manuel = players.find_one({'name': 'Manuel'})
    assert manuel['surname'] == 'Neuer'
    assert manuel['position'] == 'keeper'


def check_championships(championships):
    assert championships.count_documents({}) == 3
    check_keys_in_docs(championships, ['year', 'host', 'winner'])


def check_keys_in_docs(collection, keys):
    for doc in collection.find():
        for key in keys:
            assert key in doc


def test_insert(mongodb):
    mongodb.players.insert_one({
        'name': 'Bastian',
        'surname': 'Schweinsteiger',
        'position': 'midfield'
    })
    assert mongodb.players.count_documents({}) == 3
    assert mongodb.players.find_one({'name': 'Bastian'})


def test_mongo_engine(pytestconfig):
    assert plugin.mongo_engine() == 'mongomock'
