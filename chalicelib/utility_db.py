from bson.json_util import dumps

from pymongo import MongoClient
from werkzeug.local import LocalProxy

from chalicelib.settings import settings


# ----------------------- Db General -----------------------


# Este método se encarga de configurar la conexión con la base de datos
def get_db():
    client = MongoClient(settings.DB_URI)
    return client.get_database(settings.DB_NAME)


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def test_connection():
    return dumps(db.list_collection_names())


def collection_stats(collection_nombre):
    return dumps(db.command('collstats', collection_nombre))


def get_id_as_str(resultset):
    return str(resultset['_id'])
