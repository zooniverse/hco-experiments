
import logging

logger = logging.getLogger(__name__)


class Collection:

    def __init__(self, db):
        # pylint: disable=E1111
        self.collection = self._collection_fromdb(db._db)
        self._db = db
        self.schema = self._schema()

    #######################################################################

    @staticmethod
    def _collection_name():
        pass

    @staticmethod
    def _schema():
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

    def insert(self, data):
        self.schema.validate(data)
        self.collection.insert_one(data)

    def insert_many(self, data):
        for item in data:
            self.schema.validate(item)

        self.collection.insert_many(data)

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

    def __next__(self):
        return self.next()

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


class Schema:

    def __init__(self, schema):
        self.schema = schema

    def validate(self, obj):
        schema = self.schema
        if set(obj) != set(schema):
            raise self.SchemaValidationError.schema(obj, schema)

        for key, value in obj.items():
            type_ = schema[key].get('type', str)
            if type(type_) is type and type(value) is not type_:
                raise self.SchemaValidationError.type(obj, key, type_)

    class SchemaValidationError(Exception):

        def __init__(self, msg):
            msg = 'Attempt to upload invalid data. %s' % str(msg)
            super().__init__(msg)

        @classmethod
        def schema(cls, obj, schema):
            msg = 'Schema mismatch: %s not equal to schema %s' % \
                  (str(set(obj)), str(set(schema)))
            return cls(msg)

        @classmethod
        def missing(cls, obj, key):
            msg = 'Couldn\'t find %s in %s' % (key, str(obj))
            return cls(msg)

        @classmethod
        def type(cls, obj, key, type_):
            value = obj[key]
            msg = 'Type mismatch: %s in %s is %s, should be %s' % \
                  (key, str(obj), str(type(value)), str(type_))
            return cls(msg)
