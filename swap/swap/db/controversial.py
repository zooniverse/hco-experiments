################################################################
"""
    Ranks subjects by how controversial or agreeable they are
"""

from swap.db.db import Collection
import swap.config as config


class Controversial(Collection):

    @staticmethod
    def _collection_name():
        return 'classifications'

    def _schema(self):
        pass

    def _init_collection(self):
        pass

    #######################################################################

    def get_controversial(self, size):
        """
        Get the most controversial subjects

        Formula: :math:`(x + y) ^ {x \\over y}` where :math:`x<y`

        Parameters
        ----------
        size : int
            Number of subjects in the set
        """
        version = config.controversial_version
        query = _controv_query(size, version)
        cursor = self.aggregate(query)

        subjects = []
        for item in cursor:
            subjects.append(item['_id'])

        return subjects


    def get_consensus(self, size):
        """
        Get the most agreeable subjects, i.e. subjects with highest consensus

        Formula: :math:`(y-x) ^ {1 - {x \\over y}}` where :math:`x<y`

        Parameters
        ----------
        size : int
            Number of subjects in the set
        """
        version = config.controversial_version
        query = _consensus_query(size, version)
        cursor = self.aggregate(query)

        subjects = []
        for item in cursor:
            subjects.append(item['_id'])

        return subjects


def _controv_query(size=100, version='pow'):
    return [
        {
            '$group': {
                '_id': '$subject_id',
                'total': {'$sum': 1},
                'real': {'$sum': {'$cond': [{'$eq': ['$annotation', 1]},
                                            1, 0]}},
                'bogus': {'$sum': {'$cond': [{'$eq': ['$annotation', 0]},
                                             1, 0]}}
            }
        },
        {
            '$project': {
                '_id': 1, 'real': 1, 'bogus': 1, 'total': 1, 'controversy': {
                    '$cond': [
                        {'$gt': ['$real', '$bogus']},
                        {'$%s' % version: [
                            {'$add': ['$real', '$bogus']},
                            {'$divide': ['$bogus', '$real']}]},
                        {'$%s' % version: [
                            {'$add': ['$real', '$bogus']},
                            {'$divide': ['$real', '$bogus']}]}
                    ]
                }
            }
        },
        # {
        #     '$match': {
        #         'total': {'$lt': 50}
        #     }
        # },
        {
            '$sort': {
                'controversy': -1
            }
        },
        {
            '$limit': size
        }
    ]


def _consensus_query(size=100, version='pow'):
    return [
        {
            '$group': {
                '_id': '$subject_id',
                'total': {'$sum': 1},
                'real': {'$sum': {'$cond': [{'$eq': ['$annotation', 1]},
                                            1, 0]}},
                'bogus': {'$sum': {'$cond': [{'$eq': ['$annotation', 0]},
                                             1, 0]}}
            }
        },
        {
            '$project': {
                '_id': 1, 'real': 1, 'bogus': 1, 'total': 1, 'consensus': {
                    '$cond': [
                        {'$gt': ['$real', '$bogus']},
                        {'$%s' % version: [
                            {'$abs': {'$subtract': ['$real', '$bogus']}},
                            {'$subtract': \
                                [1, {'$divide': ['$bogus', '$real']}]}]},
                        {'$%s' % version: [
                            {'$abs': {'$subtract': ['$real', '$bogus']}},
                            {'$subtract': \
                                [1, {'$divide': ['$real', '$bogus']}]}]},
                    ]
                }
            }
        },
        # {
        #     '$match': {
        #         'total': {'$lt': 50}
        #     }
        # },
        {
            '$sort': {
                'consensus': -1
            }
        },
        {
            '$limit': size
        }
    ]
