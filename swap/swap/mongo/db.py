################################################################
# Mongo client

from swap.config import Config
from pymongo import MongoClient

class DB:
    """
        DB

        The main interaction between the python code and the 
        supporting mongo database. All calls to the database
        should be made from here.
    """

    def __init__(self):
        config = Config()

        # Get database configuration from config file
        host = config.database['host']
        db_name = config.database['name']
        port = config.database['port']

        self._client = MongoClient('%s:%d' % (host,port))
        self._db = self._client[db_name]

        self.classifications = self._db.classifications
        self.subjects = self._db.subjects
