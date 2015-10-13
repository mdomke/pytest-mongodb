import functools
import json
import os

from bson import json_util
import mongomock
import pytest
import pymongo
import yaml


_cache = {}


def pytest_addoption(parser):

    parser.addini(
        name="humongous_fixtures",
        help="Load these fixtures for tests",
        type="linelist")

    parser.addini(
        name="humongous_basedir",
        help="Try loading fixtures from this directory",
        default=os.getcwd())

    parser.addini(
        name="humongous_engine",
        help="The database engine to use [mongomock]",
        default="mongomock")

    parser.addini(
        name="humongous_host",
        help="The host where the mongodb-server runs",
        default="localhost")

    parser.addini(
        name="humongous_dbname",
        help="The name of the database where fixtures are created [humongous]",
        default="humongous")

    parser.addoption(
        "--humongous_engine",
        help="The database engine to use [mongomock]")

    parser.addoption(
        "--humongous_host",
        help="The host where the mongodb-server runs")

    parser.addoption(
        "--humongous_dbname",
        help="The name of the database where fixtures are created [humongous]")


@pytest.fixture(scope="function")
def humongous(pytestconfig):
    dbname = pytestconfig.getoption("humongous_dbname") or \
        pytestconfig.getini("humongous_dbname")
    client = make_mongo_client(pytestconfig)
    db = client[dbname]
    clean_database(db)
    load_fixtures(db, pytestconfig)
    return db


def make_mongo_client(config):
    engine = config.getoption('humongous_engine') or \
        config.getini("humongous_engine")
    host = config.getoption('humongous_host') or \
        config.getini("humongous_host")
    if engine == "pymongo":
        client = pymongo.MongoClient(host)
    else:
        client = mongomock.MongoClient(host)
    return client


def clean_database(db):
    for name in db.collection_names(include_system_collections=False):
        db.drop_collection(name)


def load_fixtures(db, config):
    basedir = config.getini("humongous_basedir")
    fixtures = config.getini("humongous_fixtures")

    for file_name in os.listdir(basedir):
        collection, ext = os.path.splitext(os.path.basename(file_name))
        selected = fixtures and collection in fixtures
        supported = ext in ("json", "yaml")
        if not selected and supported:
            continue
        path = os.path.join(basedir, file_name)
        load_fixture(db, collection, path, ext.strip("."))


def load_fixture(db, collection, path, format):
    if format == "json":
        loader = functools.partial(json.load, object_hook=json_util.object_hook)
    elif format == "yaml":
        loader = yaml.load
    else:
        return
    try:
        docs = _cache[path]
    except KeyError:
        with open(path) as fp:
            _cache[path] = docs = loader(fp)

    for document in docs:
        db[collection].insert(document)
