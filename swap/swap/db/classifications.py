################################################################
# Methods for classification collection

"""
    Manages interactions with the classification collection in the database.

    Module level variables:
        collection
            collection this module acts on
        aggregate
            reference to the pymongo aggregation method of the collection
"""

from swap.db.db import Collection, Schema
import swap.utils.parsers as parsers
import swap.config as config

from collections import OrderedDict
from pymongo import IndexModel, ASCENDING

import sys
import csv
import logging
logger = logging.getLogger(__name__)

class Classifications(Collection):

    @staticmethod
    def _collection_name():
        return 'classifications'

    @staticmethod
    def _schema():
        return Schema(config.parser.classification)

    #######################################################################

    def getClassifications(self, query=None, **kwargs):
        """
        Returns all classifications.

        Useful when running simulations of SWAP, as it returns all
        available data at once.

        Parameters
        ----------
        query : list
            Use a custom query instead
        **kwargs
            Any other variables to pass to mongo, like
            allowDiskUse, batchSize, etc
        """
        # Generate a default query if not specified

        # TODO: Parse session id if no user_id exists
        # query = [
        #     {'$sort': OrderedDict(
        #         [('seen_before', 1), ('classification_id', 1)])},
        #     {'$match': {'seen_before': False}},
        #     # {'$match': {'classification_id': {'$lt': 25000000}}},
        #     {'$project': {'user_id': 1, 'subject_id': 1,
        #                   'annotation': 1, 'session_id': 1}}
        # ]
        query = [
            {'$match': {'seen_before': False}},
            {'$sort': {'classification_id': 1}},
            # {'$match': {'classification_id': {'$lt': 25000000}}},
            {'$project': {'user_id': 1, 'subject_id': 1,
                          'annotation': 1, 'session_id': 1}}
        ]

        # set batch size as specified in kwargs,
        # or default to the config default
        if 'batch_size' in kwargs:
            batch_size = kwargs['batch_size']
        else:
            batch_size = config.database.max_batch_size
        batch_size = int(batch_size)

        # perform query on classification data
        classifications = self.aggregate(query, {'batchSize': batch_size})
        return classifications

    def _init_collection(self):
        indexes = [
            IndexModel([('subject_id', ASCENDING)]),
            IndexModel([('user_id', ASCENDING)]),
            IndexModel([('subject_id', ASCENDING), ('user_name', ASCENDING)]),
            IndexModel([('seen_before', ASCENDING),
                        ('classification_id', ASCENDING)])]

        logger.debug('inserting %d indexes', len(indexes))
        self.collection.create_indexes(indexes)
        logger.debug('done')

    def upload_project_dump(self, fname):
        logger.info('dropping collection')
        self._rebuild()

        logger.info('parsing csv dump')
        data = []
        pp = parsers.ClassificationParser('csv')

        with open(fname, 'r') as file:
            reader = csv.DictReader(file)

            for i, row in enumerate(reader):
                cl = pp.process(row)
                if cl is None:
                    continue
                data.append(cl)

                sys.stdout.flush()
                sys.stdout.write("%d records processed\r" % i)

                if len(data) > 100000:
                    self.collection.insert_many(data)
                    data = []

        self.collection.insert_many(data)
        self._gen_stats()
        logger.debug('done')

    def _gen_stats(self, upload=True):

        def count(query):
            cursor = self.aggregate(query)
            return cursor.getCount()

        nusers = count([{'$group': {'_id': '$user_name'}}])
        logger.debug('nusers: %d', nusers)

        nsubjects = count([{'$group': {'_id': '$subject_id'}}])
        logger.debug('nsubjects: %d', nsubjects)

        nclass = self.collection.count()
        logger.debug('nclass: %d', nclass)

        nclass_nodup = count([{'$match': {'seen_before': False}}])
        logger.debug('nclass_nodup: %d', nclass_nodup)

        ndup = count([{'$match': {'seen_before': True}}])

        stats = {
            'classifications': nclass,
            'users': nusers,
            'subjects': nsubjects,
            'first_classifications': nclass_nodup,
            'duplicates': ndup
        }

        logger.info('stats: %s', str(stats))
        if upload:
            logger.critical('Uploading stats')
            self._db.stats.insert_one(stats)
        return stats

    def get_stats(self):
        stats = self._db.stats
        return stats.find().sort('_id', -1).limit(1).next()

    def exists(self, classification_id):
        print(self.collection)
        logger.debug(
            'Checking if classification %d already in \'%s\'',
            classification_id, self._collection_name())
        match = {'classification_id': classification_id}

        exists = self.collection.find(match).count() > 0
        logger.debug('exists: %s', str(exists))
        return exists

    def insert(self, classification):
        id_ = classification['classification_id']
        if not self.exists(id_):
            logger.debug('Uploading classification to database')
            super().insert(classification)
