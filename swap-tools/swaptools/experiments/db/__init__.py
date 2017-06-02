
import swap.config.config as _config
from swap.utils import Singleton
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

        # Get database configuration from config file
        host = config.experiment_db.host
        db_name = config.experiment_db.name
        port = config.experiment_db.port

        self._client = MongoClient('%s:%d' % (host, port))
        self._db = self._client[db_name]
        self.batch_size = int(config.experiment_db.max_batch_size)

        self.data = self._db.data

    def setBatchSize(self, size):
        self.batch_size = size


class _Config(_config.Config):

    experiment_db = _config.Object({
        'name': 'experimentsDB',
        'host': 'localhost',
        'port': 27017,
        'max_batch_size': 1e5,
    })


class DB(_DB, metaclass=Singleton):
    pass


class Config(_Config, metaclass=Singleton):
    pass
