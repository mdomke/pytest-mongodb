.. image:: https://img.shields.io/pypi/v/pytest-mongodb.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pytest-mongodb
.. image:: https://img.shields.io/github/actions/workflow/status/mdomke/pytest-mongodb/lint-and-test.yml?branch=main&style=flat-square
    :target: https://github.com/mdomke/pytest-mongodb/actions?query=workflow%3Alint-and-test
.. image:: https://img.shields.io/pypi/l/pytest-mongodb.svg?style=flat-square
    :target: https://pypi.python.org/pypi/pytest-mongodb
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
    :target: https://black.readthedocs.io/en/stable/index.html

What is this?
=============

This is a pytest_ plugin, that enables you to test your code that relies on a database connection to
a MongoDB and expects certain data to be present.  It allows you to specify fixtures for database
collections in JSON/BSON or YAML format. Under the hood we use the mongomock_ library, that you
should consult for documentation on how to use MongoDB mock objects. If suitable you can also use a
real MongoDB server.

**Note**: This project has been renamed from ``humongous`` to ``pytest-mongodb`` in order to conform
to the pytest plugin naming convention and to be easier to find on the Python package index. See the
`migration section <Migration from humongous_>`_ for more information.


Configuration
-------------

If you don't want to put your database fixtures on the top-level directory of your package you have
to specify a directory where ``pytest-mongodb`` looks for your data definitions.

To do so put a line like the following under the ``pytest`` section of your ``pytest.ini``-file put
a

.. code-block:: ini

    [pytest]
    mongodb_fixture_dir =
      tests/unit/fixtures

``pytest-mongodb`` would then look for files ending in ``.yaml`` or ``.json`` in that directory.

If you want only a subset of the available fixtures to be loaded, you can use the ``mongodb_fixtures``
config option. It takes a list of collection file-names without the file-extension. E.g.:

.. code-block:: ini

    [pytest]
    mongodb_fixtures =
      players
      championships

In this case only the collections "players" and "championships" will be loaded.

You can also choose to use a real MongoDB server for your tests. In that case you might also want to
configure the hostname and/or the credentials if you don't want to stick with the default (localhost
and no credentials). Use the following configuration values in your ``pytest.ini`` to adapt the
settings to your needs:

.. code-block:: ini

    [pytest]
    mongodb_engine = pymongo
    mongodb_host = mongodb://user:passwd@server.tld
    mongodb_dbname = mydbname


For Mac users, who installed mongodb using homebrew, you can configure the executable to be picked up from `/usr/local/bin/mongod` instead of `/usr/local/bin/mongod` by using `mongo_exec = /usr/local/bin/mongod` in the `pytest.ini` file.

Basic usage
-----------

After you configured ``pytest-mongodb`` so that it can find your fixtures you're ready to specify
some data. Regardless of the markup language you choose, the data is provided as a list of documents
(dicts). The collection that these documents are being inserted into is given by the filename of
your fixture-file. E.g.: If you had a file named ``players.yaml`` with the following content:

.. code-block:: yaml

    - name: Mario
      surname: Götze
      position: striker

    - name: Manuel
      surname: Neuer
      position: keeper


you'd end up with a collection ``players`` that has the above player definitions inserted. If your
fixture file is in JSON/BSON format you can also use BSON specific types like ``$oid``, ``$date``,
etc.


You get ahold of the database in your test-function by using the ``mongodb`` fixture like so:

.. code-block:: python

    def test_players(mongodb):
        assert 'players' in mongodb.list_collection_names()
        manuel = mongodb.players.find_one({'name': 'Manuel'})
        assert manuel['surname'] == 'Neuer'


For further information refer to the mongomock_ documentation.

If you want to skip specific tests if the engine is ie. a mongomock engine you could do that like
so:


.. code-block:: python

    from pytest_mongodb.plugin import mongo_engine
    from pytest import mark

    @mark.skipif(mongo_engine() == 'mongomock', reason="mongomock does not support that")
    def test_players(mongodb):
        assert 'players' in mongodb.list_collection_names()
        manuel = mongodb.players.find_one({'name': 'Manuel'})
        assert manuel['surname'] == 'Neuer'


Migration from humongous
------------------------

In the course of migrating the package name from ``humongous`` to ``pytest-mongodb`` most
configuration values which previously were prefixed with ``humongous_`` have been renamed to a
``mongodb_``-prefixed counterpart. The only notable exception is the ``humongous_basedir`` config
value, which now is named ``mongodb_fixture_dir``.  Additionally the commandline options have been
unified, in a way that multi-word option names are now consistently separated with dashes instead of
underscores.


.. _mongomock: https://github.com/vmalloc/mongomock
.. _pytest: https://docs.pytest.org/en/latest/
