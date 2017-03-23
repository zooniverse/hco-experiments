################################################################
# Mongo client

from swap.config import Config
from swap.mongo.query import Query
from pymongo import MongoClient


class _DB:
    """
        DB

        The main interaction between the python code and the
        supporting mongo database. All calls to the database
        should be made from here.
    """

    def __init__(self):
        config = Config()
        self._cfg = config

        # Get database configuration from config file
        host = config.database['host']
        db_name = config.database['name']
        port = config.database['port']

        self._client = MongoClient('%s:%d' % (host, port))
        self._db = self._client[db_name]

        self.classifications = self._db.classifications
        self.subjects = self._db.subjects

    def getClassifications(self, query=None, **kwargs):
        """ Returns Iterator over all Classifications """
        # Generate a default query if not specified
        if query is None:
            query = Query()

            fields = ['user_name', 'subject_id', 'annotation', 'gold_label']
            query.project(fields)

        # set batch size as specified in kwargs,
        # or default to the config default
        batch_size = int(eval(kwargs.get(
            'batch_size',
            self._cfg.database['max_batch_size'])))

        # perform query on classification data
        classifications = self.classifications.aggregate(
            query.build(), batchSize=batch_size)

        return classifications

    def getExpertGold(self, subjects):
        query = [
            {'$group': {'_id': '$subject_id',
                        'gold': {'$first': '$gold_label'}}},
            {'$match': {'_id': {'$in': subjects}}}]

        cursor = self.classifications.aggregate(query)

        data = []
        for item in cursor:
            data.append((item['_id'], item['gold']))

        return data



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


class DB(_DB, metaclass=Singleton):
    pass
