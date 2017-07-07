
from swap.db.db import Collection
import swap.utils.parsers as parsers
import swap.config as config

import csv
import sys
from functools import wraps
import logging
logger = logging.getLogger(__name__)


def parse_golds(func):
    """
    Generates subject to gold mapping from a cursor

    Iterates through a cursor and parses out the subject to gold
    mappings.

    Parameters
    ----------
    cursor : swap.db.Cursor
        cursor containing data. Should be an aggregation containing
        one document per subject, and with the fields _id mapped to
        subject_id and gold mapped to the appropriate gold label.
    type_ : return type
        Choose the return type. Choices are:

        dict
            {_id : gold}
        tuple
            (_id, gold)
    """

    @wraps(func)
    def wrapper(self, *args, type_=dict, **kwargs):
        # build cursor from query
        query = func(self, *args, **kwargs)
        # add pipelines to use most recent gold entry
        # of each subject, and propery projections
        query += self._selection()
        cursor = self.aggregate(query)

        if type_ is dict:
            data = {}
            for item in cursor:
                id_ = item['subject']
                gold = item['gold']

                data[id_] = gold
        elif type_ is tuple:
            data = []
            for item in cursor:
                data.append((item['subject'], item['gold']))
        else:
            raise TypeError("type_ '%s' invalid type!" % str(type_))

        return data
    return wrapper


class Golds(Collection):


    @staticmethod
    def _collection_name():
        return 'subjects'

    def schema(self):
        pass

    def _init_collection(self):
        pass

    #######################################################################

    @staticmethod
    def _selection():
        return [
            {'$group': {'_id': '$subject', 'gold': {'$last': '$gold'}}},
            {'$project': {'subject': '$_id', 'gold': 1}}]

    @parse_golds
    def get_golds(self, subjects=None):
        query = []
        if subjects is not None:
            query += [{'$match': {'subject': {'$in': subjects}}}]

        return query

    @parse_golds
    def get_random_golds(self, size):
        query = [
            {'$match': {'gold': {'$ne': -1}}},
            {'$sample': {'size': size}}]

        return query

    def build_from_classifications(self):
        query = [
            {'$group': {'_id': '$subject_id',
                        'gold': {'$last': '$gold_label'}}},
            {'$project': {'subject': '$_id', 'gold': 1, '_id': 0}},
            {'$out': self._collection_name()}
        ]

        logger.critical('building gold label list from classifications')
        self._db.classifications.aggregate(query)

    def upload_golds_csv(self, fname):

        logger.info('parsing csv dump')
        data = []
        pp = parsers.GoldsParser(config.database.builder)

        with open(fname, 'r') as file:
            reader = csv.DictReader(file)

            for i, row in enumerate(reader):
                item = pp.process(row)
                if item is None:
                    continue
                data.append(item)

                sys.stdout.flush()
                sys.stdout.write("%d records processed\r" % i)

                if len(data) > 100000:
                    self.collection.insert_many(data)
                    data = []

        self.collection.insert_many(data)
        logger.debug('done')
