import functools
import json
import os
import codecs

from bson import json_util
import mongomock
import pytest
import pymongo
import yaml


_cache = {}
_engine = 'mongomock'


def pytest_addoption(parser):
    parser.addini(
        name='mongodb_fixtures',
        help='Load these fixtures for tests',
        type='linelist')

    parser.addini(
        name='mongodb_fixture_dir',
        help='Try loading fixtures from this directory',
        default=os.getcwd())

    parser.addini(
        name='mongodb_engine',
        help='The database engine to use [mongomock]',
        default='mongomock')

    parser.addini(
        name='mongodb_host',
        help='The host where the mongodb-server runs',
        default='localhost')

    parser.addini(
        name='mongodb_dbname',
        help='The name of the database where fixtures are created [pytest]',
        default='pytest')

    parser.addoption(
        '--mongodb-fixture-dir',
        help='Try loading fixtures from this directory')

    parser.addoption(
        '--mongodb-engine',
        help='The database engine to use [mongomock]')

    parser.addoption(
        '--mongodb-host',
        help='The host where the mongodb-server runs')

    parser.addoption(
        '--mongodb-dbname',
        help='The name of the database where fixtures are created [pytest]')


def pytest_configure(config):
    global _engine
    _engine = config.getoption('mongodb_engine') or config.getini('mongodb_engine')


@pytest.fixture(scope='function')
def mongodb(pytestconfig):
    dbname = pytestconfig.getoption('mongodb_dbname') or pytestconfig.getini('mongodb_dbname')
    client = make_mongo_client(pytestconfig)
    db = client[dbname]
    clean_database(db)
    load_fixtures(db, pytestconfig)
    return db


def make_mongo_client(config):
    engine = config.getoption('mongodb_engine') or config.getini('mongodb_engine')
    host = config.getoption('mongodb_host') or config.getini('mongodb_host')
    if engine == 'pymongo':
        client = pymongo.MongoClient(host)
    else:
        client = mongomock.MongoClient(host)
    return client


def clean_database(db):
    for name in list_collection_names(db):
        db.drop_collection(name)


def list_collection_names(db):
    if hasattr(db, 'list_collection_names'):
        return db.list_collection_names()
    return db.collection_names(include_system_collections=False)


def load_fixtures(db, config):
    basedir = config.getoption('mongodb_fixture_dir') or config.getini('mongodb_fixture_dir')
    if not os.path.isabs(basedir):
        basedir = config.rootdir.join(basedir).strpath
    fixtures = config.getini('mongodb_fixtures')

    for file_name in os.listdir(basedir):
        collection, ext = os.path.splitext(os.path.basename(file_name))
        file_format = ext.strip('.')
        supported = file_format in ('json', 'yaml')
        selected = collection in fixtures if fixtures else True
        if selected and supported:
            path = os.path.join(basedir, file_name)
            load_fixture(db, collection, path, file_format)


def load_fixture(db, collection, path, file_format):
    if file_format == 'json':
        loader = functools.partial(json.load, object_hook=json_util.object_hook)
    elif file_format == 'yaml':
        loader = functools.partial(yaml.load, Loader=yaml.FullLoader)
    else:
        return
    try:
        docs = _cache[path]
    except KeyError:
        with codecs.open(path, encoding='utf-8') as fp:
            _cache[path] = docs = loader(fp)
    insert_many(db[collection], docs)


def insert_many(collection, docs):
    if hasattr(collection, 'insert_many'):
        return collection.insert_many(docs)
    return collection.insert(docs)


def mongo_engine():
    return _engine
