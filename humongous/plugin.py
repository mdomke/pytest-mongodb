import json
import os

import pytest
from mongomock import Connection
import yaml


def pytest_addoption(parser):

    parser.addini(
        name="humongous_fixtures",
        help="Load these fixtures for tests",
        type="linelist")

    parser.addini(
        name="humongous_basedir",
        help="Try loading fixtures from this directory",
        default=os.getcwd())


@pytest.fixture(scope="function")
def humongous(pytestconfig):
    db = Connection().humongous
    clean_database(db)
    load_fixtures(db, pytestconfig)
    return db


def clean_database(db):
    for name in db.collection_names(include_system_collections=False):
        db.drop_collection(name)


def load_fixtures(db, config):
    basedir = config.getini("humongous_basedir")
    fixtures = config.getini("humongous_fixtures")

    for file_name in os.listdir(basedir):
        collection, ext = os.path.splitext(os.path.basename(file_name))
        selected = fixtures and collection in fixtures
        supported = ext in ["json", "yaml"]
        if not selected and supported:
            continue
        path = os.path.join(basedir, file_name)
        load_fixture(db, collection, path, ext.strip("."))


def load_fixture(db, collection, path, format):
    if format == "json":
        loader = json.load
    elif format == "yaml":
        loader = yaml.load
    else:
        return
    with open(path) as fp:
        for document in loader(fp):
            db[collection].insert(document)
