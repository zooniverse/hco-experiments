################################################################
# Mongo client

import swap.config as config
from swap.db.query import Query
from swap.utils import Singleton

from swap.db.classifications import Classifications
from swap.db.caesar import CaesarClassifications
from swap.db.golds import Golds
from swap.db.subjects import Subjects
from swap.db.controversial import Controversial

from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING
import atexit

import logging
logger = logging.getLogger(__name__)

assert Query


class _DB:
    """
        DB

        The main interaction between the python code and the
        supporting mongo database. All calls to the database
        should be made from here.
    """
    # pylint: disable=R0902

    def __init__(self):
        logger.info('opening mongo connection')

        # Get database configuration from config file
        cdb = config.database
        host = cdb.host
        db_name = cdb.name
        port = cdb.port

        self._client = MongoClient('%s:%d' % (host, port))
        self._db = self._client[db_name]
        self.batch_size = int(cdb.max_batch_size)

        self.classifications = Classifications(self)
        self.caesar = CaesarClassifications(self)
        self.subjects = Subjects(self)
        self.golds = Golds(self)
        self.controversial = Controversial(self)

        self.stats = self._db.swap_stats

    def setBatchSize(self, size):
        self.batch_size = size

    def close(self):
        logger.info('closing mongo connection')
        self._client.close()

    def _init_classifications(self):
        self.classifications._init_collection()

    def _gen_stats(self):
        self.classifications._gen_stats()

    def get_stats(self):
        return self.stats.find().sort('_id', -1).limit(1).next()


class DB(_DB, metaclass=Singleton):

    @classmethod
    def _reset(cls):
        if cls in cls._instances:
            cls._instances.pop(cls)


@atexit.register
def goodbye():
    DB().close()
