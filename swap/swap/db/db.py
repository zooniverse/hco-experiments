
import logging

logger = logging.getLogger(__name__)


class Collection:

    def __init__(self, db):
        self.collection = self._collection_fromdb(db._db)
        self._db = db

    #######################################################################

    @staticmethod
    def _collection_name():
        pass

    def schema(self):
        pass

    def _init_collection(self):
        pass

    #######################################################################

    @classmethod
    def _collection_fromdb(cls, db):
        return db[cls._collection_name()]

    def aggregate(self, query, cursor_args={}):
        if type(cursor_args) is not dict:
            raise ValueError('cursor_args must be dict: %s' % str(cursor_args))
        try:
            logger.debug('Preparing to run aggregation')
            logger.debug('query %s args %s', str(query), str(cursor_args))
            return Cursor(query, self.collection, **cursor_args)
        except Exception as e:
            logger.error(e)
            raise e

    def upload(self):
        pass

    def _drop(self):
        logger.critical('dropping collection')
        self.collection.drop()

    def _rebuild(self):
        self._drop()
        self._init_collection()


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

        logger.debug('Cursor query: %s', str(query))

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
        logger.debug(query)

        try:
            count = self.collection.aggregate(query).next()['sum']
        except StopIteration:
            count = 0
        return count

    def next(self):
        return self.cursor.next()
