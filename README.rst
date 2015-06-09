.. image:: https://img.shields.io/pypi/v/humongous.svg
    :target: https://pypi.python.org/pypi/humongous
.. image:: https://travis-ci.org/mdomke/humongous.svg?branch=master
    :target: https://travis-ci.org/mdomke/humongous
.. image:: https://img.shields.io/pypi/l/humongous.svg
    :target: https://pypi.python.org/pypi/humongous

What is this?
=============

This is a pytest plugin, that enables you to test your code that relies on a
database connection to a MongoDB and expectes certain data to be present.
It allows you to specify fixtures for database collections in JSON or YAML
format. Under the hood we use the mongomock_ library, that you should
consult for documentation on how to use MongoDB mock objects.


Configuration
-------------

If you don't want to put your fixtures on the top-level directory of your package
you have to specify a directory where `humongous` looks for your data definitions.

To do so put a line like the following under the ``pytest`` section of your
`pytest.ini`-file put a::

    [pytest]
    humongous_basedir =
      tests/unit/fixtures

`humongous` would then look for files ending in ``.yaml`` or ``.json`` in that
directory.


Basic usage
-----------

After you configured `humongous` so that it can find your fixtures you're ready to
specify some data. Regardless of the markup language you choose, the data is provided
as a list of documents (dicts). The collection that these documents are being inserted
into is given by the filename of your fixutre-file. E.g.: If you had a file named
``players.yaml`` with the following content::

    -
      name: Mario
      surname: Götze
      position: striker

    -
      name: Manuel
      surname: Neuer
      position: keeper


you'd end up with a collection `players` that has the above player definitions inserted.

You get ahold of the database in you test-function by using the ``humongous`` fixture
like so::

    def test_players(humongous):
        assert "players" in humongous.collection_names()
        manuel = humongous.players.find_one({"name": "Manuel"})
        assert manuel["surname"] == "Neuer"


For further information refer to the mongomock_ documentation.



.. _mongomock: https://github.com/vmalloc/mongomock
