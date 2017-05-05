################################################################
# Mongo client

from swap.db.query import Query
from swap.config import Config
from swap.config.helpers import Singleton
from pymongo import MongoClient

assert Query


class _DB:
    """
        DB

        The main interaction between the python code and the
        supporting mongo database. All calls to the database
        should be made from here.
    """

    def __init__(self):
        config = Config()

        # Get database configuration from config file
        cdb = config.database
        host = cdb.host
        db_name = cdb.name
        port = cdb.port

        self._client = MongoClient('%s:%d' % (host, port))
        self._db = self._client[db_name]
        self.batch_size = int(cdb.max_batch_size)

        self.classifications = self._db.classifications
        self.subjects = self._db.subjects

        self.subject_count = None

    def setBatchSize(self, size):
        self.batch_size = size


class DB(_DB, metaclass=Singleton):
    pass


class Cursor:

    def __init__(self, query, collection, **kwargs):
        self.query = query
        self.collection = collection
        self.cursor = None
        self.count = None

        if query:
            self.cursor = collection.aggregate(query, **kwargs)

    def __len__(self):
        if self.count is None:
            self.count = self.getCount()

        return self.count

    def __iter__(self):
        return self.cursor

    def getCursor(self):
        return self.cursor

    def getCount(self):
        query = self.query
        query += [{'$group': {'_id': 1, 'sum': {'$sum': 1}}}]

        count = self.collection.aggregate(query).next()['sum']
        return count

    def next(self):
        return self.cursor.next()
