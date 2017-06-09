################################################################
# Mongo client
# !! DEPRECATED !!
# Use swap.db instead

from swap.mongo.query import Query
import swap.config as config
from pymongo import MongoClient


class _DB:
    """
        DB

        The main interaction between the python code and the
        supporting mongo database. All calls to the database
        should be made from here.
    """

    def __init__(self):
        self._cfg = config

        # Get database configuration from config file
        host = config.database.host
        db_name = config.database.name
        port = config.database.port

        self._client = MongoClient('%s:%d' % (host, port))
        self._db = self._client[db_name]
        self.batch_size = int(self._cfg.database.max_batch_size)

        self.classifications = self._db.classifications
        self.subjects = self._db.subjects

        self.subject_count = None

    def setBatchSize(self, size):
        self.batch_size = size

    def getClassifications(self, query=None, **kwargs):
        """ Returns Iterator over all Classifications """
        # Generate a default query if not specified
        if query is None:
            query = Query()

            fields = ['user_name', 'subject_id', 'annotation']
            query.project(fields)

        # set batch size as specified in kwargs,
        # or default to the config default
        batch_size = kwargs.get(
            'batch_size',
            self.batch_size)

        # perform query on classification data
        classifications = Cursor(query.build(), self.classifications,
                                 batchSize=batch_size)
        # classifications = self.classifications.aggregate(
        #     query.build(), batchSize=batch_size)

        return classifications

    def getExpertGold(self, subjects):
        query = [
            {'$group': {'_id': '$subject_id',
                        'gold': {'$first': '$gold_label'}}},
            {'$match': {'_id': {'$in': subjects}}}]

        cursor = self.classifications.aggregate(query)

        data = {}
        for item in cursor:
            data[item['_id']] = item['gold']

        return data

    def getAllGolds(self):
        query = [
            {'$group': {'_id': '$subject_id',
                        'gold': {'$first': '$gold_label'}}}]

        return Cursor(query, self.classifications)

    def getRandomGoldSample(self, size):
        query = [
            {'$group': {'_id': '$subject_id',
                        'gold': {'$first': '$gold_label'}}},
            {'$sample': {'size': size}}]

        return Cursor(query, self.classifications)

    def getNSubjects(self):
        if self.subject_count is None:
            query = [
                {'$group': {'_id': '', 'num': {'$sum': 1}}}]
            cursor = self.classifications.aggregate(query)
            self.subject_count = cursor.next()['num']

        return self.subject_count

    def getUserAgent(self, user_id):
        pass

    def putUserAgent(self, user_agent):
        pass

    def getSubjectAgent(self, subject_id):
        pass

    def putSubjectAgent(self, subject_id):
        pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls)\
                .__call__(*args, **kwargs)
        return cls._instances[cls]

    def _reset_instances(cls):
        cls._instances = {}


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
