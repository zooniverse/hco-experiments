################################################################
# Mongo client

from swap.db.query import Query
from swap.config import Config
from swap.utils import Singleton
from pymongo import MongoClient

import atexit

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
        self.experiment = self._db.experiment
        self.subjects = self._db.subjects

        self.subject_count = None

    def setBatchSize(self, size):
        self.batch_size = size

    def close(self):
        self._client.close()


class DB(_DB, metaclass=Singleton):
    pass


class Cursor:
    """
    Custom wrapper around mongo's aggregation cursor.

    Has additional functionality to get the number of documents
    in a query, which is not otherwise available from the regular cursor.
    However, this functionality performs an additional query to mongo,
    so it comes with a slight penalty due to additional network access.
    """

    def __init__(self, query, collection, **kwargs):
        """
        Parameters
        ----------
        query : list
            Aggregation query for mongo
        collection : swap.db.[collection]
            Collection the query thould be performed on
        **kargs
            Additional parameters that are passed to the pymongo aggregation
            command
        """
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


@atexit.register
def goodbye():
    DB().close()
